# Migratsiyalar

Bu papka ataylab bo'sh qoldirilgan. Birinchi migratsiyani real PostgreSQL bazasiga ulanib,
avtomatik generatsiya qilish tavsiya etiladi (qo'lda yozilgan sxema migratsiyasi modeldan
uzilib qolish xavfini keltirib chiqaradi):

```bash
# 1) .env faylida DATABASE_URL (yoki POSTGRES_*) to'g'ri sozlanganiga ishonch hosil qiling
# 2) pg_trgm kengaytmasi (fuzzy FIO qidiruvi uchun) — DB superuser tomonidan bir marta:
psql "$DATABASE_URL" -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"

# 3) Birinchi migratsiyani generatsiya qiling
alembic revision --autogenerate -m "initial schema"

# 4) Qo'llang
alembic upgrade head

# 5) Sobit rollarni (SuperAdmin/HR/Rahbariyat/IT) urug'lang
python scripts/seed_roles.py
```

`pg_trgm` kengaytmasi ataylab alembic migratsiyasi ichida emas, balki alohida bosqichda
ishlatiladi — `CREATE EXTENSION` odatda DB superuser huquqini talab qiladi, ilova
ulanadigan oddiy DB foydalanuvchisida bu huquq bo'lmasligi mumkin (ko'plab boshqariladigan
PostgreSQL xizmatlarida ham shunday).
