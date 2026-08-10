# Desktop wrapper (Windows 10/11) — Tauri

Bu — rasmiy `create-tauri-app` generatori orqali yaratilgan **haqiqiy, ishlaydigan** Tauri v2
loyihasi (qo'lda taxmin qilingan boshlang'ich kod emas). `src-tauri/` mavjud `../frontend`
Vue ilovasiga ishora qiladi — bu papkada alohida frontend yo'q, chunki asosiy frontend
allaqachon `frontend/`da mavjud.

Loyiha shu muhitda haqiqatan ham qurib (build qilib) ko'rilgan: `cargo check` va
`npm run tauri build` ikkalasi ham muvaffaqiyatli o'tdi (Rust: rustup orqali o'rnatildi,
WebView2 va MSVC build vositalari kompyuterda allaqachon mavjud edi).

## Nega Tauri

- O'rnatuvchi hajmi Electron'nikidan ~10-20 marta kichik (Chromium o'rniga OS-native
  WebView2'dan foydalanadi).
- Hujum yuzasi kamroq — Node.js runtime konteynerga o'ralib yubordirilmaydi.
- `tauri.conf.json` orqali qat'iy Content-Security-Policy o'rnatilgan (`app.security.csp`).

**Windows 7 haqida:** WebView2'ning Win7/8/8.1'dagi oxirgi versiyasi 109 — 2022-yil
dekabrdan beri xavfsizlik yamoqlarisiz muzlab qolgan. Tauri'ning o'zida "minimal Windows
versiyasi" degan alohida sozlama yo'q (buni tekshirdim — `bundle.windows` sxemasida bunday
maydon mavjud emas); shu sababli cheklov `bundle.windows.minimumWebview2Version`ni
`110.0.0.0`ga o'rnatish orqali amalga oshirilgan — bu WebView2'ning Win7/8'da mavjud bo'la
oladigan oxirgi (109) versiyasidan yuqori, ya'ni amalda faqat joriy WebView2'ga ega
Win10/11 kompyuterlarda to'g'ri ishlaydi. Win7 mashinalar veb-ilovani (`frontend/`)
to'g'ridan-to'g'ri brauzer orqali ishlatishda davom etadi.

## Talablar

- Node.js (frontend uchun, allaqachon `frontend/`da o'rnatilgan bo'lishi kerak)
- Rust (rustup orqali): https://rustup.rs/ — yoki Windows'da `winget install Rustlang.Rustup`
- Windows uchun: Microsoft Visual C++ Build Tools (odatda Visual Studio bilan birga keladi)
  va WebView2 Runtime (Windows 10/11'da odatda oldindan o'rnatilgan bo'ladi)

## Ishga tushirish

```bash
cd desktop
npm install
npm run tauri dev
```

Bu buyruq avtomatik ravishda `../frontend`da dev-serverni ishga tushiradi
(`beforeDevCommand`, `tauri.conf.json`ga qarang) va Tauri oynasini ochadi.

## Tarqatish uchun qurish (.msi / .exe)

```bash
cd desktop
npm run tauri build
```

Bu avval `../frontend`ni production uchun quradi (`beforeBuildCommand`), so'ng Rust
kodini release rejimida kompilyatsiya qilib, quyidagi joyga o'rnatuvchi fayllarni chiqaradi:

```
desktop/src-tauri/target/release/bundle/
├── msi/Kadr_0.1.0_x64_en-US.msi
└── nsis/Kadr_0.1.0_x64-setup.exe
```

## Nimalarni o'zgartirish kerak (ishlab chiqarishga o'tishdan oldin)

- **`src-tauri/icons/`** — hozircha Tauri'ning standart namunaviy belgisi (icon). Tashkilot
  logotipini qo'yish uchun: `npm run tauri icon path/to/logo.png` (kamida 1024x1024 PNG).
- **`tauri.conf.json` → `app.security.csp`** — `connect-src`dagi `http://localhost:8000`
  ishlab chiqarish backend manzili bilan almashtirilishi kerak (masalan
  `https://kadr.tashkilot.uz`).
- **`Cargo.toml` → `[package] authors`** — tashkilot nomi bilan yangilang.
