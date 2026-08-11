@echo off
REM Backend serverni lokal kompyuterda ishga tushiradi (PostgreSQL allaqachon
REM ishlab turgan va backend\.env sozlangan bo'lishi kerak).
cd /d "%~dp0"
call .venv\Scripts\activate.bat
uvicorn app.main:app --host 127.0.0.1 --port 8000
