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

    /// `postgres.exe` uchun — unga Rust'ning o'zi `Child` sifatida spawn qilmagani
    /// sababli (`postgres.rs`dagi izohga q. — to'g'ridan-to'g'ri spawn qilish
    /// Administrator tekshiruviga uchraydi), PID orqali vaqtinchalik tutqich ochib,
    /// Job Object'ga biriktiramiz, so'ng shu tutqichning o'zini yopamiz (biriktirish
    /// doimiy — Job o'z ichida kuzatib turadi, mahalliy tutqichni ushlab turish shart
    /// emas).
    pub fn assign_pid(&self, pid: u32) -> Result<(), String> {
        use windows::Win32::Foundation::CloseHandle;
        use windows::Win32::System::Threading::{OpenProcess, PROCESS_SET_QUOTA, PROCESS_TERMINATE};

        unsafe {
            let handle = OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, false, pid)
                .map_err(|e| format!("postgres jarayoniga (PID {pid}) tutqich ochilmadi: {e}"))?;
            let result = self
                .job
                .assign_process(handle.0 as _)
                .map_err(|e| format!("postgres Job Object'ga biriktirilmadi: {e}"));
            let _ = CloseHandle(handle);
            result
        }
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

    pub fn assign_pid(&self, _pid: u32) -> Result<(), String> {
        Ok(())
    }
}
