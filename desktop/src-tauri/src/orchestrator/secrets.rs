use serde::{Deserialize, Serialize};
use std::path::Path;
use std::process::{Command, Stdio};

#[cfg(windows)]
use std::os::windows::process::CommandExt;
#[cfg(windows)]
const CREATE_NO_WINDOW: u32 = 0x0800_0000;

/// Har bir o'rnatish uchun bir martalik generatsiya qilinadigan maxfiy qiymatlar.
/// Birinchi ishga tushirishda generatsiya qilinib, `secrets.json`ga yoziladi; keyingi
/// har bir ishga tushirishda o'sha fayldan o'qiladi (bazaga mos kelishi shart, chunki
/// `FIELD_ENCRYPTION_KEY` o'zgarsa avval shifrlangan PINFL/pasport ma'lumotlari o'qib
/// bo'lmay qoladi).
#[derive(Serialize, Deserialize, Clone)]
pub struct Secrets {
    pub postgres_superuser_password: String,
    pub postgres_app_password: String,
    pub secret_key: String,
    pub field_encryption_key: String,
}

/// Fernet kaliti (32 tasodifiy bayt, base64) kabi maxsus formatlarni Rust'da qayta
/// amalga oshirish keraksiz xavf — buning o'rniga allaqachon vendorlangan Python
/// interpretatoridan (va uning `cryptography` kutubxonasidan) bir martalik
/// chaqiruv orqali foydalanamiz. Parollar esa faqat hex belgilardan iborat —
/// `bootstrap.py`ning DDL literal xavfsizligi shuni talab qiladi.
const GENERATE_SCRIPT: &str = r#"import secrets, json
from cryptography.fernet import Fernet
print(json.dumps({
    "postgres_superuser_password": secrets.token_hex(24),
    "postgres_app_password": secrets.token_hex(24),
    "secret_key": secrets.token_hex(32),
    "field_encryption_key": Fernet.generate_key().decode(),
}))
"#;

pub fn load_or_generate(secrets_file: &Path, python_exe: &Path) -> Result<Secrets, String> {
    if secrets_file.exists() {
        let content =
            std::fs::read_to_string(secrets_file).map_err(|e| format!("maxfiy fayl o'qilmadi: {e}"))?;
        return serde_json::from_str(&content).map_err(|e| format!("maxfiy fayl buzilgan: {e}"));
    }

    let mut cmd = Command::new(python_exe);
    cmd.arg("-c").arg(GENERATE_SCRIPT);
    #[cfg(windows)]
    cmd.creation_flags(CREATE_NO_WINDOW);
    cmd.stdin(Stdio::null());

    let output = cmd
        .output()
        .map_err(|e| format!("maxfiy qiymatlarni generatsiya qilib bo'lmadi (python topilmadimi?): {e}"))?;
    if !output.status.success() {
        return Err(format!(
            "maxfiy qiymatlarni generatsiya qilishda xato: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let secrets: Secrets =
        serde_json::from_str(stdout.trim()).map_err(|e| format!("generatsiya natijasi noto'g'ri format: {e}"))?;

    let json = serde_json::to_string_pretty(&secrets).map_err(|e| e.to_string())?;
    std::fs::write(secrets_file, json).map_err(|e| format!("maxfiy fayl yozilmadi: {e}"))?;

    Ok(secrets)
}
