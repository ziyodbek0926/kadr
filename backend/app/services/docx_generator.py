"""Xodim ma'lumotlari asosida "Obyektivka" (.docx) hujjatini python-docx bilan generatsiya
qilish. Bu — dastlabki (boshlang'ich) kod strukturasi: aniq tashkilotning rasmiy shabloni
mavjud bo'lsa, `templates/README.md`da tavsiya etilganidek docxtpl + tayyor .docx shabloniga
o'tish ishlab chiqarish uchun qulayroq. Employee obyekti chaqirilishdan oldin barcha
bog'liq to'plamlari (relatives/education_history/...) yuklangan bo'lishi kerak
(app.crud.employee.CRUDEmployee.get_detail orqali)."""

import re
from datetime import date
from io import BytesIO

import nh3
from docx import Document
from docx.document import Document as DocxDocument
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from app.models.employee import Employee


_RELATION_LABELS = {
    "father": "Otasi",
    "mother": "Onasi",
    "spouse": "Turmush o'rtog'i",
    "child": "Farzandi",
    "sibling": "Aka/uka, opa/singlisi",
    "other": "Boshqa qarindosh",
}
_GENDER_LABELS = {"male": "Erkak", "female": "Ayol"}
_EDUCATION_LEVEL_LABELS = {
    "secondary": "O'rta",
    "secondary_special": "O'rta-maxsus",
    "bachelor": "Bakalavr",
    "master": "Magistr",
    "phd": "Fan doktori/nomzodi",
}
_EMPLOYMENT_STATUS_LABELS = {
    "active": "Faoliyat yuritmoqda",
    "on_leave": "Ta'til/dam olishda",
    "dismissed": "Bo'shatilgan",
}


def _strip_html(value: str | None) -> list[str]:
    """Rich-text maydonini oddiy paragraflarga aylantiradi — python-docx HTML'ni o'zi
    render qila olmaydi. Qiymat odatda app.utils.sanitize orqali saqlashdan oldin
    tozalangan bo'ladi, lekin bu yerda YANA nh3 orqali o'tkaziladi (ikkinchi himoya
    qatlami): oddiy regex bilan teg olib tashlansa, `<script>alert(1)</script>` kabi
    holatlarda teg o'chadi-yu, ICHIDAGI matn ("alert(1)") qolib ketadi — nh3 esa
    script/style kabi xavfli elementlarni mazmuni bilan birga olib tashlaydi (faqat
    "p"/"br" ruxsat etilgan holda ham). Bu masalan scripts/import_from_access.py kabi
    Pydantic validatsiyasini chetlab o'tuvchi yo'llar orqali tozalanmagan matn bazaga
    tushib qolgan taqdirda ham hujjatga xavfli/chalkash matn chiqmasligini kafolatlaydi.
    "p"/"br" ataylab ruxsat etiladi — ular paragraf chegaralarini saqlab qoladi, keyin
    pastda newline'ga aylantiriladi."""
    if not value:
        return []
    safe_html = nh3.clean(value, tags={"p", "br"})
    text = re.sub(r"<br\s*/?>", "\n", safe_html)
    text = re.sub(r"</p\s*>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return [line.strip() for line in text.split("\n") if line.strip()]


def _format_date(value: date | None) -> str:
    return value.strftime("%d.%m.%Y") if value else "—"


def _set_base_style(document: DocxDocument) -> None:
    style = document.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    section = document.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1.5)


def _add_field(document: DocxDocument, label: str, value: str) -> None:
    p = document.add_paragraph()
    run_label = p.add_run(f"{label}: ")
    run_label.bold = True
    p.add_run(value or "—")


def _add_table(document: DocxDocument, headers: list[str], rows: list[list[str]]) -> None:
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, header in enumerate(headers):
        cell = table.rows[0].cells[idx]
        cell.text = header
        cell.paragraphs[0].runs[0].bold = True
    for row in rows:
        cells = table.add_row().cells
        for idx, value in enumerate(row):
            cells[idx].text = value


def generate_objektivka(employee: Employee) -> BytesIO:
    document = Document()
    _set_base_style(document)

    title = document.add_heading("OBYEKTIVKA", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle = document.add_paragraph(employee.full_name.upper())
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.runs[0].bold = True
    subtitle.runs[0].font.size = Pt(14)

    if employee.position:
        pos_line = document.add_paragraph(f"{employee.position.title} — {employee.position.department.name}")
        pos_line.alignment = WD_ALIGN_PARAGRAPH.CENTER

    document.add_paragraph()

    _add_field(document, "Tug'ilgan sana", _format_date(employee.birth_date))
    _add_field(document, "Tug'ilgan joyi", employee.birth_place or "—")
    _add_field(document, "Jinsi", _GENDER_LABELS.get(employee.gender.value, employee.gender.value))
    _add_field(document, "Millati", employee.nationality or "—")
    _add_field(document, "Fuqaroligi", employee.citizenship or "—")
    _add_field(document, "Joriy manzili", employee.current_address or "—")
    _add_field(document, "Doimiy yashash manzili", employee.permanent_address or "—")
    _add_field(document, "Telefon raqami", employee.phone_number or "—")
    _add_field(document, "Ishga qabul qilingan sana", _format_date(employee.hire_date))
    _add_field(document, "Joriy lavozimda ishlay boshlagan sana", _format_date(employee.position_since))
    _add_field(
        document,
        "Holati",
        _EMPLOYMENT_STATUS_LABELS.get(employee.employment_status.value, employee.employment_status.value),
    )

    document.add_heading("Ta'lim to'g'risida ma'lumot", level=2)
    if employee.education_history:
        _add_table(
            document,
            ["O'quv muassasasi", "Mutaxassisligi", "Daraja", "Davri", "Hujjat №"],
            [
                [
                    edu.institution_name,
                    edu.specialty or "—",
                    _EDUCATION_LEVEL_LABELS.get(edu.level.value, edu.level.value),
                    f"{_format_date(edu.start_date)} — {_format_date(edu.end_date)}",
                    edu.document_number or "—",
                ]
                for edu in employee.education_history
            ],
        )
    else:
        document.add_paragraph("Ma'lumot kiritilmagan.")

    document.add_heading("Mehnat faoliyati", level=2)
    if employee.work_history:
        _add_table(
            document,
            ["Tashkilot", "Lavozim", "Davri", "Buyruq asosida"],
            [
                [
                    wh.organization_name,
                    wh.position_title,
                    f"{_format_date(wh.start_date)} — {_format_date(wh.end_date) if wh.end_date else 'hozirgacha'}",
                    wh.order_reference or "—",
                ]
                for wh in employee.work_history
            ],
        )
    else:
        document.add_paragraph("Ma'lumot kiritilmagan.")

    document.add_heading("Yaqin qarindoshlari", level=2)
    if employee.relatives:
        _add_table(
            document,
            ["Qarindoshlik", "F.I.Sh.", "Tug'ilgan yili", "Ish joyi / lavozimi", "Manzili"],
            [
                [
                    _RELATION_LABELS.get(rel.relation_type.value, rel.relation_type.value),
                    rel.full_name,
                    str(rel.birth_year) if rel.birth_year else "—",
                    f"{rel.workplace or '—'} / {rel.position_title or '—'}",
                    rel.address or "—",
                ]
                for rel in employee.relatives
            ],
        )
    else:
        document.add_paragraph("Ma'lumot kiritilmagan.")

    document.add_heading("Davlat mukofotlari", level=2)
    if employee.awards:
        _add_table(
            document,
            ["Mukofot nomi", "Sanasi", "Tavsiya etgan tashkilot"],
            [
                [award.name, _format_date(award.awarded_date), award.recommending_organization or "—"]
                for award in employee.awards
            ],
        )
    else:
        document.add_paragraph("Mukofotlari yo'q.")

    if employee.foreign_trips:
        document.add_heading("Xorijga chiqishlari", level=2)
        _add_table(
            document,
            ["Davlat", "Maqsadi", "Davri", "Asos hujjat"],
            [
                [
                    trip.country,
                    trip.purpose or "—",
                    f"{_format_date(trip.start_date)} — {_format_date(trip.end_date)}",
                    trip.order_basis or "—",
                ]
                for trip in employee.foreign_trips
            ],
        )

    positive_lines = _strip_html(employee.positive_traits)
    if positive_lines:
        document.add_heading("Ijobiy fazilatlari", level=2)
        for line in positive_lines:
            document.add_paragraph(line)

    negative_lines = _strip_html(employee.negative_traits)
    if negative_lines:
        document.add_heading("Salbiy fazilatlari / tanqidiy fikrlar", level=2)
        for line in negative_lines:
            document.add_paragraph(line)

    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer
