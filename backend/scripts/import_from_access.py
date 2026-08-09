import argparse
import asyncio
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.database import AsyncSessionLocal
from app.core.security import encrypt_field, hash_lookup_value
from app.models.employee import Employee
from app.models.enums import EmploymentStatus, Gender

COLUMN_MAP = {
    "Familiya": "last_name",
    "Ism": "first_name",
    "Sharif": "middle_name",
    "TugilganSana": "birth_date",
    "TugilganJoy": "birth_place",
    "Jinsi": "gender",
    "Millati": "nationality",
    "JSHSHIR": "pinfl",
    "Manzil": "current_address",
    "Telefon": "phone_number",
}

_GENDER_MAP = {"эркак": Gender.MALE, "erkak": Gender.MALE, "аёл": Gender.FEMALE, "ayol": Gender.FEMALE}
_REQUIRED_FIELDS = ("last_name", "first_name", "birth_date")


def _parse_row(row: "pd.Series") -> dict:
    data: dict = {}
    for excel_col, field in COLUMN_MAP.items():
        if excel_col not in row or pd.isna(row[excel_col]):
            continue
        data[field] = row[excel_col]

    if "birth_date" in data and not isinstance(data["birth_date"], date):
        data["birth_date"] = pd.to_datetime(data["birth_date"]).date()

    if "gender" in data:
        data["gender"] = _GENDER_MAP.get(str(data["gender"]).strip().lower(), Gender.MALE)

    data.setdefault("employment_status", EmploymentStatus.ACTIVE)
    return data


async def _import_rows(rows: list[dict], *, dry_run: bool) -> None:
    async with AsyncSessionLocal() as db:
        imported, skipped = 0, 0
        for data in rows:
            if any(field not in data for field in _REQUIRED_FIELDS):
                skipped += 1
                continue

            pinfl = data.pop("pinfl", None)
            if pinfl:
                data["pinfl_encrypted"] = encrypt_field(str(int(pinfl)) if isinstance(pinfl, float) else str(pinfl))
                data["pinfl_hash"] = hash_lookup_value(str(int(pinfl)) if isinstance(pinfl, float) else str(pinfl))

            if not dry_run:
                db.add(Employee(**data))
            imported += 1

        mode = "tekshirildi (dry-run, bazaga yozilmadi)" if dry_run else "import qilindi"
        print(f"Tayyor: {imported} ta yozuv {mode}, {skipped} ta o'tkazib yuborildi (majburiy maydon yo'q).")

        if not dry_run:
            await db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Cadry5L Excel eksportini PostgreSQL'ga import qilish")
    parser.add_argument("--file", required=True, help="Access'dan eksport qilingan .xlsx fayl yo'li")
    parser.add_argument("--sheet", default=0, help="Excel varag'i nomi/raqami")
    parser.add_argument("--dry-run", action="store_true", help="Faqat tekshiradi, bazaga yozmaydi")
    args = parser.parse_args()

    df = pd.read_excel(args.file, sheet_name=args.sheet)
    rows = [_parse_row(row) for _, row in df.iterrows()]

    asyncio.run(_import_rows(rows, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
