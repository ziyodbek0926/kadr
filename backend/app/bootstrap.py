"""Standalone o'rnatuvchi uchun: ilova roli/bazasi/`pg_trgm` kengaytmasi/sxema/sobit
rollarni bitta chaqiruv bilan tayyorlaydi. Idempotent — mavjud narsalarni qayta
yaratishga urinmaydi, shu sabab har ishga tushirishda (nafaqat birinchi marta) xavfsiz
qayta bajariladi. Markazlashgan/Docker joylashtirishda ISHLATILMAYDI — u yerda
migratsiya/urug'lash hamon qo'lda (`backend/alembic/versions/README.md`dagidek), chunki
u yerda DB allaqachon boshqa vosita (masalan tashkilot IT bo'limi) tomonidan boshqariladi.

Barcha maxfiy qiymatlar (superuser paroli, ilova roli paroli — `Settings.POSTGRES_PASSWORD`
orqali) CHAQIRUVCHI tomonidan (standalone rejimda — Rust orkestratori) oldindan
generatsiya qilinib, muhit o'zgaruvchilari orqali uzatiladi. Bu modul hech qanday maxfiy
qiymat generatsiya QILMAYDI, faqat ularni ishlatadi.

Ishga tushirish: `python -m app.bootstrap`
Talab qilinadigan qo'shimcha muhit o'zgaruvchilari (odatiy Settings maydonlaridan tashqari):
  POSTGRES_SUPERUSER          — bootstrap uchun superuser roli nomi (odatiy: "postgres")
  POSTGRES_SUPERUSER_PASSWORD — shu superuserning paroli (majburiy)
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import asyncpg
from alembic.config import Config

from alembic import command
from app.core.config import settings

_ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic.ini"


def _require_safe_password(value: str, field_name: str) -> None:
    """`CREATE ROLE ... PASSWORD '<literal>'` parametrlashtirishni qo'llab-quvvatlamaydi
    (DDL) — parol SQL literal sifatida to'g'ridan-to'g'ri qo'yiladi. Shu sabab faqat
    chaqiruvchi tomonidan generatsiya qilingan, so'z-raqamli (hex/urlsafe) parollargagina
    ishonamiz — tirnoq yoki nuqta-vergul kabi belgilar bo'lsa, aniq xato bilan to'xtaymiz
    (jim ravishda noto'g'ri SQL yasashdan ko'ra xavfsizroq)."""
    if not value or not value.replace("-", "").replace("_", "").isalnum():
        raise ValueError(
            f"{field_name} faqat harf/raqam (va '-'/'_') dan iborat bo'lishi shart — "
            "DDL'da xavfsiz literal sifatida qo'yish uchun"
        )


async def _ensure_role_and_database(superuser: str, superuser_password: str) -> None:
    _require_safe_password(settings.POSTGRES_PASSWORD, "POSTGRES_PASSWORD")
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=superuser,
        password=superuser_password,
        database="postgres",
    )
    try:
        role_exists = await conn.fetchval("SELECT 1 FROM pg_roles WHERE rolname = $1", settings.POSTGRES_USER)
        if not role_exists:
            await conn.execute(f'CREATE ROLE "{settings.POSTGRES_USER}" LOGIN PASSWORD \'{settings.POSTGRES_PASSWORD}\'')
            print(f"Rol yaratildi: {settings.POSTGRES_USER}")
        else:
            print(f"Rol allaqachon mavjud: {settings.POSTGRES_USER}")

        db_exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", settings.POSTGRES_DB)
        if not db_exists:
            await conn.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}" OWNER "{settings.POSTGRES_USER}"')
            print(f"Baza yaratildi: {settings.POSTGRES_DB}")
        else:
            print(f"Baza allaqachon mavjud: {settings.POSTGRES_DB}")
    finally:
        await conn.close()


async def _ensure_extension(superuser: str, superuser_password: str) -> None:
    """`pg_trgm` — FIO bo'yicha imlo xatosiga chidamli qidiruv uchun (GIN indeks,
    birinchi migratsiyaning o'zida ishlatiladi — shu sabab bu migratsiyadan OLDIN
    bajarilishi shart, aks holda `alembic upgrade head` o'zi muvaffaqiyatsiz tugaydi).
    Kengaytma superuser huquqini talab qiladi — ilovaning o'z roli buni qila olmaydi."""
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=superuser,
        password=superuser_password,
        database=settings.POSTGRES_DB,
    )
    try:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        print("pg_trgm kengaytmasi tayyor.")
    finally:
        await conn.close()


def _run_migrations() -> None:
    """Diqqat: bu SOF (sync) funksiya — `alembic/env.py` ichida o'zi
    `asyncio.run(...)` chaqiradi, shu sabab buni allaqachon ishlab turgan event loop
    ICHIDAN chaqirib bo'lmaydi ("asyncio.run() cannot be called from a running event
    loop"). Shu sabab `main()`da bu boshqa `asyncio.run(...)` chaqiruvlari bilan
    ARALASH emas, ketma-ket, alohida bajariladi."""
    cfg = Config(str(_ALEMBIC_INI))
    cfg.set_main_option("script_location", str(_ALEMBIC_INI.parent / "alembic"))
    command.upgrade(cfg, "head")
    print("Migratsiyalar head'gacha qo'llandi.")


def main() -> None:
    superuser = os.environ.get("POSTGRES_SUPERUSER", "postgres")
    superuser_password = os.environ.get("POSTGRES_SUPERUSER_PASSWORD")
    if not superuser_password:
        print("POSTGRES_SUPERUSER_PASSWORD muhit o'zgaruvchisi berilmagan.", file=sys.stderr)
        raise SystemExit(1)

    try:
        asyncio.run(_ensure_role_and_database(superuser, superuser_password))
        asyncio.run(_ensure_extension(superuser, superuser_password))
        _run_migrations()

        from scripts.seed_roles import seed_roles

        asyncio.run(seed_roles())
    except Exception as exc:
        print(f"Bootstrap xato bilan tugadi: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print("Bootstrap tayyor.")


if __name__ == "__main__":
    main()
