use std::path::Path;
use std::process::{Command, Stdio};

#[cfg(windows)]
use std::os::windows::process::CommandExt;
#[cfg(windows)]
const CREATE_NO_WINDOW: u32 = 0x0800_0000;

fn base_command(exe: &Path) -> Command {
    let mut cmd = Command::new(exe);
    #[cfg(windows)]
    cmd.creation_flags(CREATE_NO_WINDOW);
    cmd
}

/// `pgdata/PG_VERSION` — Postgres'ning o'zi yaratadigan fayl, "bu papka allaqachon
/// ishga tayyor baza" degani. Alohida "men bootstrap qilganman" belgisi o'rniga aynan
/// shuni tekshiramiz — ikkinchisi oldingi urinish yarim to'xtagan holatda haqiqatdan
/// chetlashib qolishi mumkin edi.
pub fn ensure_initialized(pgsql_bin: &Path, pgdata: &Path, superuser_password: &str) -> Result<(), String> {
    if pgdata.join("PG_VERSION").exists() {
        return Ok(());
    }
    std::fs::create_dir_all(pgdata).map_err(|e| format!("pgdata papkasi yaratilmadi: {e}"))?;

    // Parol CLI argumentida EMAS, vaqtinchalik faylda — aks holda Task Manager/`ps`
    // orqali boshqa jarayonlar buni ko'rishi mumkin edi.
    let pwfile = pgdata
        .parent()
        .ok_or("pgdata ota-papkasi topilmadi")?
        .join("_pw_init.tmp");
    std::fs::write(&pwfile, superuser_password).map_err(|e| format!("vaqtinchalik parol fayli yozilmadi: {e}"))?;

    let mut cmd = base_command(&pgsql_bin.join("initdb.exe"));
    cmd.arg("-D")
        .arg(pgdata)
        .arg("-U")
        .arg("postgres")
        .arg("--pwfile")
        .arg(&pwfile)
        .arg("--auth=scram-sha-256")
        .arg("-E")
        .arg("UTF8")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    let output = cmd.output().map_err(|e| format!("initdb ishga tushmadi: {e}"))?;
    let _ = std::fs::remove_file(&pwfile);

    if !output.status.success() {
        return Err(format!("initdb muvaffaqiyatsiz: {}", String::from_utf8_lossy(&output.stderr)));
    }
    Ok(())
}

/// `pg_ctl start -w` server tayyor bo'lguncha o'zi kutadi — alohida "health" so'rovi
/// yozish shart emas, Postgres buni ichkarida allaqachon qiladi.
pub fn start(pgsql_bin: &Path, pgdata: &Path, port: u16, log_file: &Path) -> Result<(), String> {
    let mut cmd = base_command(&pgsql_bin.join("pg_ctl.exe"));
    cmd.arg("start")
        .arg("-D")
        .arg(pgdata)
        .arg("-w")
        .arg("-t")
        .arg("60")
        .arg("-l")
        .arg(log_file)
        .arg("-o")
        .arg(format!("-p {port}"))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    let output = cmd.output().map_err(|e| format!("pg_ctl start ishga tushmadi: {e}"))?;
    if !output.status.success() {
        return Err(format!(
            "PostgreSQL ishga tushmadi (log: {}): {}",
            log_file.display(),
            String::from_utf8_lossy(&output.stderr)
        ));
    }
    Ok(())
}

/// `-m fast -w` — mijozlarni kutmasdan, lekin baribir TOZA (WAL flush qilingan)
/// to'xtatadi va tugaguncha kutadi. `-w`siz `pg_ctl stop` darhol qaytadi, Postgres esa
/// fonda hali to'xtayotgan bo'ladi — Job Object bilan birga ishlatilganda buni buzadi
/// (jarayon "toza" tugashidan oldin yo'q qilinishi mumkin).
pub fn stop(pgsql_bin: &Path, pgdata: &Path) {
    let mut cmd = base_command(&pgsql_bin.join("pg_ctl.exe"));
    cmd.arg("stop")
        .arg("-D")
        .arg(pgdata)
        .arg("-m")
        .arg("fast")
        .arg("-w")
        .arg("-t")
        .arg("30")
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    let _ = cmd.status();
}
