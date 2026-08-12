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
    // GUI-subsystem ilovada (Tauri, konsolsiz) meros qilib olinadigan stdin yaroqsiz —
    // ba'zi bola jarayonlar (pg_ctl ichida ishga tushiriladigan postgres.exe) shu
    // holatda o'qishga urinib abadiy to'xtab qolishi mumkin (haqiqiy sinovda pg_ctl
    // start hech qachon qaytmasligi kuzatildi — sabab aynan shu edi).
    cmd.stdin(Stdio::null());
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

/// `pg_ctl start -w` server tayyor bo'lguncha o'zi kutadi. `postgres.exe`ni
/// to'g'ridan-to'g'ri spawn qilish (Job Object uchun `Child` tutqichi olish maqsadida)
/// SINALGAN va RAD ETILGAN: Postgres "Execution of PostgreSQL by a user with
/// administrative permissions is not permitted" xatosi bilan ishga tushishni rad
/// etadi — bu Administrator token ostidagi jarayonlarga Postgres'ning o'zi qo'yadigan
/// qat'iy xavfsizlik cheklovi (o'zgartirib bo'lmaydi). Qiziq jihati: xuddi shu muhitda
/// `pg_ctl start` orqali ishga tushirilganda bu xato CHIQMAYDI — shu sabab bu yerda
/// pg_ctl saqlab qolinadi, Job Object uchun kerakli PID esa keyinroq (`read_postmaster_pid`)
/// `postmaster.pid` faylidan o'qib olinadi (pg_ctl bergan `Child` emas — u faqat
/// pg_ctl'ning o'zini ifodalaydi, ICHKARIDA ishga tushirilgan postgres.exe'ni emas).
///
/// `Stdio::piped()` ATAYLAB ishlatilmaydi: `pg_ctl start` muvaffaqiyatli bo'lganda
/// ICHKARIDA uzoq umr ko'radigan `postgres.exe`ni ishga tushiradi — shu bola jarayon
/// bizning stdout/stderr pipe tutqichimizni MEROS qilib oladi va uni hech qachon
/// yopmaydi (chunki postgres.exe tugamaydi). Natijada `pg_ctl.exe`ning o'zi
/// allaqachon muvaffaqiyatli chiqib ketgan bo'lsa ham, pipe'da EOF hech qachon
/// kelmaydi va `.output()` ABADIY osilib qoladi — haqiqiy sinovda aynan shu sodir
/// bo'ldi. `-l log_file` orqali Postgres'ning haqiqiy chiqishi allaqachon fayl
/// orqali olinadi — xato bo'lsa, o'sha logdan o'qiymiz.
pub fn start(pgsql_bin: &Path, pgdata: &Path, port: u16, log_file: &Path) -> Result<u32, String> {
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
        .stdout(Stdio::null())
        .stderr(Stdio::null());

    let status = cmd.status().map_err(|e| format!("pg_ctl start ishga tushmadi: {e}"))?;
    if !status.success() {
        let log_tail = std::fs::read_to_string(log_file)
            .map(|s| s.lines().rev().take(15).collect::<Vec<_>>().into_iter().rev().collect::<Vec<_>>().join("\n"))
            .unwrap_or_else(|_| "(log fayli o'qilmadi)".to_string());
        return Err(format!("PostgreSQL ishga tushmadi (log: {}):\n{log_tail}", log_file.display()));
    }
    read_postmaster_pid(pgdata)
}

/// `pg_ctl start` muvaffaqiyatli tugagach, haqiqiy `postgres.exe`ning PID'i
/// `pgdata/postmaster.pid` faylining BIRINCHI qatorida yotadi (Postgres'ning o'zi
/// yozadi) — buni Job Object'ga biriktirish uchun ishlatamiz.
fn read_postmaster_pid(pgdata: &Path) -> Result<u32, String> {
    let content = std::fs::read_to_string(pgdata.join("postmaster.pid"))
        .map_err(|e| format!("postmaster.pid o'qilmadi: {e}"))?;
    content
        .lines()
        .next()
        .and_then(|line| line.trim().parse::<u32>().ok())
        .ok_or_else(|| "postmaster.pid'dan PID o'qib bo'lmadi".to_string())
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
