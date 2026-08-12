//! Standalone rejim orkestratori — bu modul faqat JARAYONLARNI boshqaradi (ishga
//! tushirish/kutish/to'xtatish). Barcha SQL/DB-bilimli mantiq (rol/baza/`pg_trgm`
//! yaratish, migratsiya, urug'lash) ATAYLAB bu yerda emas, `backend/app/bootstrap.py`da
//! — Postgres bilan ishlash uchun kerakli vositalar (asyncpg, alembic, ORM modellari)
//! allaqachon Python tomonda mavjud va sinalgan.

mod backend;
mod job;
mod paths;
mod secrets;
mod postgres;

use paths::AppPaths;
use std::path::PathBuf;
use std::process::Child;
use std::time::Duration;
use tauri::AppHandle;

const POSTGRES_PORT: u16 = 55432;
const BACKEND_PORT: u16 = 8000;
const HEALTH_TIMEOUT: Duration = Duration::from_secs(45);

pub struct RunningServices {
    backend_child: Child,
    pgsql_bin: PathBuf,
    pgdata: PathBuf,
    #[cfg(windows)]
    _job: job::ProcessGuard,
}

/// Postgres'ni (kerak bo'lsa `initdb` bilan) va backend'ni ketma-ket ishga tushiradi,
/// `/health` javob berguncha kutadi. Har qanday bosqichda xato bo'lsa, o'shanga qadar
/// ishga tushirilgan narsalarni orqaga qaytarib (to'xtatib) xato bilan chiqadi — yarim
/// ishlagan holatda qoldirmaslik uchun.
pub fn start_all(app: &AppHandle) -> Result<RunningServices, String> {
    let paths = AppPaths::resolve(app)?;
    let secrets = secrets::load_or_generate(&paths.secrets_file, &paths.python_exe)?;

    postgres::ensure_initialized(&paths.pgsql_bin_dir, &paths.pgdata_dir, &secrets.postgres_superuser_password)?;
    postgres::start(&paths.pgsql_bin_dir, &paths.pgdata_dir, POSTGRES_PORT, &paths.pg_log_file)?;

    let backend_env = backend::BackendEnv {
        python_exe: &paths.python_exe,
        postgres_port: POSTGRES_PORT,
        postgres_superuser_password: &secrets.postgres_superuser_password,
        postgres_password: &secrets.postgres_app_password,
        upload_dir: &paths.upload_dir,
        backend_port: BACKEND_PORT,
    };

    if let Err(e) = backend::run_bootstrap(&backend_env, &secrets.secret_key, &secrets.field_encryption_key) {
        postgres::stop(&paths.pgsql_bin_dir, &paths.pgdata_dir);
        return Err(e);
    }

    let child = match backend::spawn_server(
        &backend_env,
        &secrets.secret_key,
        &secrets.field_encryption_key,
        &paths.backend_log_file,
    ) {
        Ok(c) => c,
        Err(e) => {
            postgres::stop(&paths.pgsql_bin_dir, &paths.pgdata_dir);
            return Err(e);
        }
    };

    let job = match job::ProcessGuard::new() {
        Ok(j) => j,
        Err(e) => {
            let mut child = child;
            let _ = child.kill();
            postgres::stop(&paths.pgsql_bin_dir, &paths.pgdata_dir);
            return Err(e);
        }
    };
    if let Err(e) = job.assign(&child) {
        let mut child = child;
        let _ = child.kill();
        postgres::stop(&paths.pgsql_bin_dir, &paths.pgdata_dir);
        return Err(e);
    }

    if let Err(e) = backend::wait_healthy(BACKEND_PORT, HEALTH_TIMEOUT) {
        let mut child = child;
        let _ = child.kill();
        postgres::stop(&paths.pgsql_bin_dir, &paths.pgdata_dir);
        return Err(e);
    }

    Ok(RunningServices {
        backend_child: child,
        pgsql_bin: paths.pgsql_bin_dir,
        pgdata: paths.pgdata_dir,
        #[cfg(windows)]
        _job: job,
    })
}

/// Toza to'xtatish tartibi: avval backend (so'rovlarni tugatishga imkon berish uchun
/// alohida kutishning ma'nosi yo'q — FastAPI'da graceful-shutdown handler yo'q, shu
/// sabab to'g'ridan-to'g'ri o'ldiramiz), keyin Postgres `-m fast -w` bilan (WAL flush
/// qilib, TO'LIQ to'xtaguncha kutadi).
pub fn stop_all(services: &mut RunningServices) {
    let _ = services.backend_child.kill();
    let _ = services.backend_child.wait();
    postgres::stop(&services.pgsql_bin, &services.pgdata);
}
