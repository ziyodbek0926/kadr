from io import BytesIO

import pandas as pd

from app.models.employee import Employee

_EMPLOYMENT_STATUS_LABELS = {
    "active": "Faoliyat yuritmoqda",
    "on_leave": "Ta'til/dam olishda",
    "dismissed": "Bo'shatilgan",
}
_GENDER_LABELS = {"male": "Erkak", "female": "Ayol"}


def export_employees_to_excel(employees: list[Employee]) -> BytesIO:
    """Qidiruv/ro'yxat natijalarini Excel hisobotiga eksport qiladi."""
    rows = [
        {
            "F.I.Sh.": emp.full_name,
            "Tug'ilgan sana": emp.birth_date,
            "Jinsi": _GENDER_LABELS.get(emp.gender.value, emp.gender.value),
            "Bo'lim": emp.position.department.name if emp.position else "—",
            "Lavozim": emp.position.title if emp.position else "—",
            "Joriy lavozimda": emp.position_since,
            "Holati": _EMPLOYMENT_STATUS_LABELS.get(emp.employment_status.value, emp.employment_status.value),
            "Mutaxassislik sohasi": emp.specialization_area or "—",
            "Telefon": emp.phone_number or "—",
        }
        for emp in employees
    ]
    df = pd.DataFrame(rows)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Xodimlar")
        worksheet = writer.sheets["Xodimlar"]
        for column_cells in worksheet.columns:
            length = max((len(str(cell.value)) for cell in column_cells if cell.value is not None), default=10)
            worksheet.column_dimensions[column_cells[0].column_letter].width = min(length + 2, 40)

    buffer.seek(0)
    return buffer
