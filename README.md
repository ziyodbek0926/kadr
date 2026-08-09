# Kadr — Kadrlar boshqaruvi tizimi

"Cadry5L" (MS Access) o'rnini bosuvchi markazlashgan, veb-asosli kadrlar boshqaruvi
tizimi. Maqsad — ma'lumotlarni fleshkada tashish amaliyotini yo'q qilib, xavfsiz,
tezkor va bir markazdan boshqariladigan platforma yaratish.

To'liq texnik topshiriq: [`docs/TZ_Kadrlar_Tizimi.docx`](docs/TZ_Kadrlar_Tizimi.docx)

## Texnologik stek

| Qatlam | Texnologiya | Sabab |
|---|---|---|
| Backend | FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL + Alembic | Avtomatik OpenAPI hujjatlari, Pydantic'ning qattiq validatsiyasi, async I/O |
| Frontend | Vue 3 + TypeScript + Tailwind CSS + Pinia | Kichik jamoa uchun o'qish/qo'llab-quvvatlash osonligi, yengil bundle |
| Desktop (ixtiyoriy) | Tauri v2 (Win10/11) | WebView2-asosli, kichik o'rnatuvchi, kichik hujum yuzasi |
| Hujjatlar | python-docx (.docx), pandas/openpyxl (.xlsx) | So'ralgan standart kutubxonalar |

## Papka tuzilishi

```
kadr/
├── backend/        FastAPI ilova (app/), Alembic migratsiyalari, skriptlar
├── frontend/        Vue 3 SPA
├── desktop/          Tauri wrapper uchun ko'rsatma va namuna konfiguratsiya
├── deploy/            Ishlab chiqarish uchun nginx (TLS) namunasi
├── docker-compose.yml
└── docs/               TZ, loyiha prompt hujjati, arxitektura
```

## Ishga tushirish (lokal, Docker'siz)

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          
pip install -r requirements-dev.txt
copy .env.example .env          # so'ng SECRET_KEY / FIELD_ENCRYPTION_KEY / POSTGRES_* ni to'ldiring
```

`SECRET_KEY` va `FIELD_ENCRYPTION_KEY` generatsiya qilish:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

PostgreSQL'ga ulanib, `pg_trgm` kengaytmasini yoqing (bir marta, superuser sifatida),
so'ng migratsiyalarni generatsiya/qo'llang va sobit rollarni urug'lang — batafsil:
[`backend/alembic/versions/README.md`](backend/alembic/versions/README.md).

```bash
uvicorn app.main:app --reload
```

Swagger hujjatlari: `http://localhost:8000/api/v1/docs`

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

`http://localhost:5173`

### 3. Desktop wrapper (ixtiyoriy, Win10/11)

[`desktop/README.md`](desktop/README.md)ga qarang.

## Docker Compose bilan (barchasi birga)

```bash
copy backend\.env.example backend\.env   
docker compose up --build
```

Ishlab chiqarish muhitida bu konteynerlar oldiga TLS tugatuvchi teskari-proksi
qo'yish tavsiya etiladi — namuna: [`deploy/nginx.conf.example`](deploy/nginx.conf.example).

## Eski Access ma'lumotlarini ko'chirish

```bash
cd backend
python scripts/import_from_access.py --file eski_xodimlar.xlsx --dry-run
```

Batafsil: [`backend/scripts/import_from_access.py`](backend/scripts/import_from_access.py) docstring'i.

## Xavfsizlik — qisqacha

- JWT (qisqa umrli access + httpOnly cookie'dagi refresh), Argon2 parol xeshlash
- Har bir endpoint'da rol tekshiruvi (`require_role`) — backend'da majburiy
- PINFL/pasport — Fernet bilan shifrlangan holda saqlanadi, alohida HMAC-hash orqali qidiriladi
- Rich-text maydonlar `nh3` bilan sanitizatsiya qilinadi (saqlangan XSS'dan himoya)
- Advanced Search — whitelist asosida, xom SQL/ustun nomi hech qachon qabul qilinmaydi
- Har bir create/update/delete audit-logga yoziladi
- Login endpoint rate-limit qilingan (`slowapi`), hisob bir necha muvaffaqiyatsiz urinishdan keyin vaqtincha bloklanadi

To'liq ro'yxat va asoslash: TZ hujjatining "Xavfsizlik arxitekturasi" bo'limi.
