use std::path::PathBuf;
use tauri::{AppHandle, Manager};

/// Standalone rejimda kerak bo'ladigan barcha fayl yo'llari — bittalik joyda, shu sabab
/// orkestratsiyaning qolgan qismi "qayerda nima yotibdi"ni bilishi shart emas.
pub struct AppPaths {
    pub pgdata_dir: PathBuf,
    pub secrets_file: PathBuf,
    pub upload_dir: PathBuf,
    pub pg_log_file: PathBuf,
    pub backend_log_file: PathBuf,
    pub pgsql_bin_dir: PathBuf,
    pub python_exe: PathBuf,
}

impl AppPaths {
    pub fn resolve(app: &AppHandle) -> Result<Self, String> {
        // Foydalanuvchi-yozish huquqiga ega joy — "Program Files" ostida initdb/uploads
        // ishlamaydi (standart Windows ACL faqat o'qish/bajarishga ruxsat beradi).
        let app_data_dir = app
            .path()
            .app_data_dir()
            .map_err(|e| format!("app-data-dir topilmadi: {e}"))?;
        std::fs::create_dir_all(&app_data_dir).map_err(|e| format!("app-data-dir yaratilmadi: {e}"))?;
        // Postgres'ga argument sifatida uzatiladigan yo'llar ham xuddi shu sababdan
        // (yuqoridagi izohga q.) soddalashtiriladi.
        let app_data_dir = dunce::simplified(&app_data_dir).to_path_buf();

        let log_dir = app_data_dir.join("logs");
        std::fs::create_dir_all(&log_dir).map_err(|e| format!("log papkasi yaratilmadi: {e}"))?;

        let upload_dir = app_data_dir.join("uploads");
        std::fs::create_dir_all(&upload_dir).map_err(|e| format!("uploads papkasi yaratilmadi: {e}"))?;

        // vendor/pyruntime va vendor/pgsql — tauri.conf.json'dagi bundle.resources orqali
        // shu resurs papkasi ostiga joylashtiriladi (src-tauri/ ICHIDA saqlangani uchun
        // Tauri'ning _up_/_root_ escaping'iga uchramaydi).
        //
        // `dunce::simplified` — Tauri'ning resource_dir()'i ba'zan `\\?\`-prefiksli
        // uzun-yo'l (UNC extended-length) formatida qaytaradi; initdb.exe kabi C
        // dasturlari argv[0]'dan qo'shni dasturni (postgres.exe) qidirishda bu formatni
        // to'g'ri tushunmay, "topilmadi" deb xato beradi (haqiqiy sinovda duch kelindi).
        let resource_dir = app
            .path()
            .resource_dir()
            .map_err(|e| format!("resource-dir topilmadi: {e}"))?;
        let resource_dir = dunce::simplified(&resource_dir).to_path_buf();
        let vendor_dir = resource_dir.join("vendor");

        Ok(Self {
            pgdata_dir: app_data_dir.join("pgdata"),
            secrets_file: app_data_dir.join("secrets.json"),
            pg_log_file: log_dir.join("postgres.log"),
            backend_log_file: log_dir.join("backend.log"),
            pgsql_bin_dir: vendor_dir.join("pgsql").join("bin"),
            python_exe: vendor_dir.join("pyruntime").join("python.exe"),
            upload_dir,
        })
    }
}
