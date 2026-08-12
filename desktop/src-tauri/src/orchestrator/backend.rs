use std::collections::HashMap;
use std::path::Path;
use std::process::{Child, Command, Stdio};
use std::time::{Duration, Instant};

#[cfg(windows)]
use std::os::windows::process::CommandExt;
#[cfg(windows)]
const CREATE_NO_WINDOW: u32 = 0x0800_0000;

/// Backend'ga uzatiladigan barcha muhit o'zgaruvchilari — `.env` fayli ATAYLAB
/// ishlatilmaydi (`app.core.config.Settings` uni topa olmasa CWD'ga bog'liq bo'lib
/// qoladi), o'rniga hammasi shu yerdan aniq uzatiladi.
pub struct BackendEnv<'a> {
    pub python_exe: &'a Path,
    pub postgres_port: u16,
    pub postgres_superuser_password: &'a str,
    pub postgres_password: &'a str,
    pub upload_dir: &'a Path,
    pub backend_port: u16,
}

fn env_map(env: &BackendEnv) -> HashMap<&'static str, String> {
    let mut m = HashMap::new();
    m.insert("POSTGRES_HOST", "127.0.0.1".to_string());
    m.insert("POSTGRES_PORT", env.postgres_port.to_string());
    m.insert("POSTGRES_USER", "kadr_app".to_string());
    m.insert("POSTGRES_PASSWORD", env.postgres_password.to_string());
    m.insert("POSTGRES_DB", "kadr".to_string());
    m.insert("POSTGRES_SUPERUSER", "postgres".to_string());
    m.insert("POSTGRES_SUPERUSER_PASSWORD", env.postgres_superuser_password.to_string());
    // SECRET_KEY/FIELD_ENCRYPTION_KEY quyida chaqiruvchi (mod.rs) tomonidan qo'shiladi —
    // BackendEnv'ga ularni ikki marta saqlamaslik uchun shu funksiyaga kirmagan.
    m.insert("UPLOAD_DIR", env.upload_dir.to_string_lossy().to_string());
    m.insert("MAX_UPLOAD_SIZE_MB", "10".to_string());
    m.insert("LOGIN_RATE_LIMIT", "20/minute".to_string());
    // Standalone rejimda backend faqat shu Tauri oynasiga xizmat qiladi — CORS ro'yxati
    // WebView2'ning haqiqiy Origin'iga mos (tauri.conf.json'dagi bilan bir xil eslatma:
    // http EMAS, https ham EMAS — aynan shu uch shakl kerak).
    m.insert(
        "BACKEND_CORS_ORIGINS",
        r#"["http://tauri.localhost","tauri://localhost","https://tauri.localhost"]"#.to_string(),
    );
    m
}

pub fn run_bootstrap(env: &BackendEnv, secret_key: &str, field_encryption_key: &str) -> Result<(), String> {
    let mut cmd = Command::new(env.python_exe);
    cmd.arg("-m").arg("app.bootstrap");
    #[cfg(windows)]
    cmd.creation_flags(CREATE_NO_WINDOW);
    for (k, v) in env_map(env) {
        cmd.env(k, v);
    }
    cmd.env("SECRET_KEY", secret_key);
    cmd.env("FIELD_ENCRYPTION_KEY", field_encryption_key);
    cmd.stdout(Stdio::piped()).stderr(Stdio::piped());

    let output = cmd.output().map_err(|e| format!("bootstrap ishga tushmadi: {e}"))?;
    if !output.status.success() {
        return Err(format!(
            "Bootstrap muvaffaqiyatsiz: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }
    Ok(())
}

/// Uzoq umr ko'radigan (app yopilguncha ishlaydigan) backend jarayoni — chaqiruvchi
/// `Child`ni saqlab qo'yishi kerak, aks holda to'xtatib bo'lmaydi.
pub fn spawn_server(
    env: &BackendEnv,
    secret_key: &str,
    field_encryption_key: &str,
    log_file: &Path,
) -> Result<Child, String> {
    let log_out = std::fs::File::create(log_file).map_err(|e| format!("log fayli yaratilmadi: {e}"))?;
    let log_err = log_out.try_clone().map_err(|e| format!("log fayli nusxalanmadi: {e}"))?;

    let mut cmd = Command::new(env.python_exe);
    cmd.arg("-m")
        .arg("uvicorn")
        .arg("app.main:app")
        .arg("--host")
        .arg("127.0.0.1")
        .arg("--port")
        .arg(env.backend_port.to_string());
    #[cfg(windows)]
    cmd.creation_flags(CREATE_NO_WINDOW);
    for (k, v) in env_map(env) {
        cmd.env(k, v);
    }
    cmd.env("SECRET_KEY", secret_key);
    cmd.env("FIELD_ENCRYPTION_KEY", field_encryption_key);
    cmd.stdout(Stdio::from(log_out)).stderr(Stdio::from(log_err));

    cmd.spawn().map_err(|e| format!("backend ishga tushmadi: {e}"))
}

pub fn wait_healthy(port: u16, timeout: Duration) -> Result<(), String> {
    let url = format!("http://127.0.0.1:{port}/health");
    let deadline = Instant::now() + timeout;

    loop {
        if let Ok(response) = ureq::get(&url).call() {
            if response.status() == 200 {
                return Ok(());
            }
        }
        if Instant::now() >= deadline {
            return Err(format!(
                "Backend {} soniya ichida javob bermadi (log fayllarini tekshiring)",
                timeout.as_secs()
            ));
        }
        std::thread::sleep(Duration::from_millis(300));
    }
}
