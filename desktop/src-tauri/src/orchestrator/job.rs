//! Windows Job Object — asosiy `.exe` qulasa yoki Task Manager'dan majburan
//! o'chirilsa ham, unga tayinlangan bola jarayonlar (`postgres.exe`, `python.exe`)
//! yetim qolib, `pgdata`ni qulflab qolmasligi uchun ofat-holat zaxira chorasi. Bu
//! TOZA to'xtatishning o'rnini bosmaydi — faqat qulash holatida ishlaydi (batafsil
//! izoh `mod.rs`da).

#[cfg(windows)]
use std::os::windows::io::AsRawHandle;
#[cfg(windows)]
use win32job::Job;

#[cfg(windows)]
pub struct ProcessGuard {
    job: Job,
}

#[cfg(windows)]
impl ProcessGuard {
    pub fn new() -> Result<Self, String> {
        let job = Job::create().map_err(|e| format!("Job Object yaratilmadi: {e}"))?;
        let mut info = job
            .query_extended_limit_info()
            .map_err(|e| format!("Job Object ma'lumoti o'qilmadi: {e}"))?;
        info.limit_kill_on_job_close();
        job.set_extended_limit_info(&mut info)
            .map_err(|e| format!("Job Object sozlanmadi: {e}"))?;
        Ok(Self { job })
    }

    pub fn assign(&self, child: &std::process::Child) -> Result<(), String> {
        self.job
            .assign_process(child.as_raw_handle() as _)
            .map_err(|e| format!("jarayon Job Object'ga biriktirilmadi: {e}"))
    }
}

#[cfg(not(windows))]
pub struct ProcessGuard;

#[cfg(not(windows))]
impl ProcessGuard {
    pub fn new() -> Result<Self, String> {
        Ok(Self)
    }

    pub fn assign(&self, _child: &std::process::Child) -> Result<(), String> {
        Ok(())
    }
}
