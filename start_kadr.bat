@echo off
REM "Kadr" tizimini lokal kompyuterda to'liq ishga tushiradi: backend serverni
REM alohida oynada ko'taradi, so'ng desktop-ilovani ochadi.
REM Talab: PostgreSQL xizmati ishlab turishi kerak (Windows xizmatlari ro'yxatida
REM "postgresql-x64-18" holati "Running" bo'lsin).

cd /d "%~dp0"

echo Backend server ishga tushirilmoqda (alohida oynada)...
start "Kadr backend" cmd /k "cd backend && start_local.bat"

timeout /t 3 /nobreak >nul

echo Desktop ilova ochilmoqda...
start "" "desktop\src-tauri\target\release\kadr-desktop.exe"
