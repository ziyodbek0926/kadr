from datetime import date

from docx import Document

from app.models.employee import Employee
from app.models.enums import EmploymentStatus, Gender
from app.services.docx_generator import generate_objektivka


def _make_employee(**overrides) -> Employee:
    defaults = {
        "last_name": "Aliyev",
        "first_name": "O'ktam",
        "middle_name": "Bahodir o'g'li",
        "birth_date": date(1990, 5, 12),
        "birth_place": "Toshkent",
        "gender": Gender.MALE,
        "employment_status": EmploymentStatus.ACTIVE,
    }
    defaults.update(overrides)
    return Employee(**defaults)


def test_generates_valid_docx_zip_container() -> None:
    buf = generate_objektivka(_make_employee())
    data = buf.read()
    assert data[:2] == b"PK"
    assert len(data) > 0


def test_script_tag_content_is_not_leaked_into_document() -> None:
    employee = _make_employee(
        positive_traits="<p>Masuliyatli</p><script>alert(document.cookie)</script>",
    )
    doc = Document(generate_objektivka(employee))
    full_text = "\n".join(p.text for p in doc.paragraphs)

    assert "alert" not in full_text
    assert "document.cookie" not in full_text
    assert "Masuliyatli" in full_text


def test_paragraph_boundaries_are_preserved() -> None:
    employee = _make_employee(positive_traits="<p>Birinchi jumla</p><p>Ikkinchi jumla</p>")
    doc = Document(generate_objektivka(employee))
    paragraph_texts = [p.text for p in doc.paragraphs if p.text.strip()]

    assert "Birinchi jumla" in paragraph_texts
    assert "Ikkinchi jumla" in paragraph_texts
    assert "Birinchi jumlaIkkinchi jumla" not in paragraph_texts
