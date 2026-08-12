mod orchestrator;

use std::sync::Mutex;
use tauri::Manager;

struct AppState {
    services: Mutex<Option<orchestrator::RunningServices>>,
}

#[cfg(windows)]
fn show_startup_error(message: &str) {
    use windows::core::PCWSTR;
    use windows::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_ICONERROR, MB_OK};

    eprintln!("Kadr — ishga tushirishda xatolik: {message}");

    let body = format!(
        "Dastur ishga tushmadi:\n\n{message}\n\nBatafsil: %APPDATA%\\uz.gov.kadr.desktop\\logs\\\0"
    );
    let title = "Kadr — ishga tushirishda xatolik\0";
    let body_wide: Vec<u16> = body.encode_utf16().collect();
    let title_wide: Vec<u16> = title.encode_utf16().collect();

    unsafe {
        MessageBoxW(
            None,
            PCWSTR(body_wide.as_ptr()),
            PCWSTR(title_wide.as_ptr()),
            MB_OK | MB_ICONERROR,
        );
    }
}

#[cfg(not(windows))]
fn show_startup_error(message: &str) {
    eprintln!("Kadr — ishga tushirishda xatolik: {message}");
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(AppState {
            services: Mutex::new(None),
        })
        .setup(|app| {
            // Postgres+backend'ni orqa oqimda ishga tushiramiz — asosiy oyna darhol
            // ko'rinadi (OS "javob bermayapti" holatiga chiqarmaslik uchun), bitta-marta
            // (odatda ~2-15s, birinchi ishga tushirishda `initdb`+migratsiyalar tufayli
            // ko'proq) sozlash tugagach xodim login qila oladi.
            let handle = app.handle().clone();
            std::thread::spawn(move || match orchestrator::start_all(&handle) {
                Ok(services) => {
                    let state = handle.state::<AppState>();
                    *state.services.lock().expect("services mutex buzilgan") = Some(services);
                }
                Err(e) => show_startup_error(&e),
            });
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                // Postgres'ni `-m fast` bilan ham bo'lsa TO'XTAGUNCHA kutish kerak —
                // shu sabab oynani darhol yopib yubormaymiz, avval fon oqimda toza
                // to'xtatib, keyin o'zimiz chiqamiz.
                api.prevent_close();
                let app = window.app_handle().clone();
                std::thread::spawn(move || {
                    let state = app.state::<AppState>();
                    let services = state.services.lock().expect("services mutex buzilgan").take();
                    if let Some(mut services) = services {
                        orchestrator::stop_all(&mut services);
                    }
                    app.exit(0);
                });
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
