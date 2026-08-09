# Desktop wrapper (Windows 10/11) — Tauri

Bu papka qo'lda yozilgan Rust boshlang'ich kodini o'z ichiga OLMAYDI. Tauri loyihasini
qo'lda (Cargo.toml/main.rs) qurish o'rniga rasmiy CLI orqali generatsiya qilish tavsiya
etiladi — versiyalar tez o'zgaradi, qo'lda yozilgan boshlang'ich kod tezda eskiradi va
xavfsizlik yamoqlarini o'zi kuzatib borish qiyin.

## Nega Tauri

- O'rnatuvchi hajmi Electron'nikidan ~10-20 marta kichik (Chromium o'rniga OS-native
  WebView2'dan foydalanadi).
- Hujum yuzasi kamroq — Node.js runtime konteynerga o'ralib yubordirilmaydi.
- `tauri.conf.json` orqali qat'iy Content-Security-Policy o'rnatish oson.

**Windows 7 haqida:** WebView2'ning Win7/8/8.1'dagi oxirgi versiyasi 109 — 2022-yil
dekabrdan beri xavfsizlik yamoqlarisiz muzlab qolgan. Shu sababli bu wrapper build
konfiguratsiyasida ataylab faqat **Windows 10/11** minimal versiya sifatida ko'rsatiladi.
Win7 mashinalar veb-ilovani (frontend/) to'g'ridan-to'g'ri brauzer orqali ishlatishda
davom etadi — asosiy TZ hujjatidagi arxitektura qarorlariga qarang.

## Sozlash qadamlari

1. Rust va Tauri talablarini o'rnating: https://tauri.app/start/prerequisites/
2. Ushbu papkada CLI orqali generatsiya qiling:
   ```
   npm create tauri-app@latest
   ```
   "Existing project" / "vanilla" rejimini tanlang, chunki frontend allaqachon
   `../frontend` papkasida alohida Vue loyihasi sifatida mavjud.
3. Generatsiya qilingan `src-tauri/tauri.conf.json`ni shu papkadagi
   `tauri.conf.example.json` namunasidagi `build`/`bundle` qiymatlariga qarab sozlang
   (frontend build chiqishi, CSP, Windows minimal versiyasi).
4. Ishga tushirish (frontend dev-server parallel ishlab turishi kerak):
   ```
   npm run tauri dev
   ```
5. Tarqatish uchun `.msi`/`.exe (nsis)` qurish:
   ```
   npm run tauri build
   ```
