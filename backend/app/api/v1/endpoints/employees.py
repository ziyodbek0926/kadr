from typing import Annotated, TypeVar

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse

from app.api.v1.deps import AdminUser, CurrentUser, DbSession, EditorUser, client_ip
from app.core.database import Base
from app.core.security import decrypt_field
from app.crud.award import award_crud
from app.crud.document_attachment import document_attachment_crud
from app.crud.education_history import education_history_crud
from app.crud.employee import employee_crud
from app.crud.foreign_trip import foreign_trip_crud
from app.crud.relative import relative_crud
from app.crud.work_history import work_history_crud
from app.models.award import Award
from app.models.document_attachment import DocumentAttachment
from app.models.education_history import EducationHistory
from app.models.employee import Employee
from app.models.foreign_trip import ForeignTrip
from app.models.relative import Relative
from app.models.work_history import WorkHistory
from app.schemas.award import AwardCreate, AwardRead, AwardUpdate
from app.schemas.document_attachment import DocumentAttachmentRead
from app.schemas.education_history import EducationHistoryCreate, EducationHistoryRead, EducationHistoryUpdate
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeDetailRead,
    EmployeeListItem,
    EmployeeSensitiveRead,
    EmployeeUpdate,
)
from app.schemas.foreign_trip import ForeignTripCreate, ForeignTripRead, ForeignTripUpdate
from app.schemas.relative import RelativeCreate, RelativeRead, RelativeUpdate
from app.schemas.work_history import WorkHistoryCreate, WorkHistoryRead, WorkHistoryUpdate
from app.services.audit_service import model_snapshot, record_audit
from app.services.file_storage import UploadValidationError, delete_attachment_file, resolve_stored_path, save_attachment

router = APIRouter()

_ChildModel = TypeVar("_ChildModel", bound=Base)

# EditorUser/AdminUser — app.api.v1.deps'da ta'riflangan (butun API bo'ylab qayta ishlatiladi).
# Oddiy o'qish (list/detail) barcha autentifikatsiyadan o'tgan rollarga ochiq (Rahbariyat ham
# kiradi, chunki uning huquqi faqat o'qish bilan cheklangan — yozish endpoint'lari EditorUser/
# AdminUser talab qiladi, Rahbariyat rolining kodi ular ro'yxatida yo'q).


async def _get_employee_or_404(db: DbSession, employee_id: int) -> Employee:
    employee = await employee_crud.get(db, employee_id)
    if employee is None or employee.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Xodim topilmadi")
    return employee


async def _get_detail_or_500(db: DbSession, employee_id: int) -> Employee:
    # create/update endpoint'lari o'zi hozirgina yozgan yozuvni shu tranzaksiya ichida
    # qayta o'qiydi — shuning uchun None amalda kelmasligi kerak; baribir aniq xato bilan
    # himoyalanadi, "get_detail() -> Employee | None" kontraktini yashirin buzmaslik uchun.
    employee = await employee_crud.get_detail(db, employee_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kutilmagan xato: hozirgina saqlangan yozuv topilmadi",
        )
    return employee


async def _get_owned_or_404(
    db: DbSession, model: type[_ChildModel], item_id: int, employee_id: int
) -> _ChildModel:
    """Bola yozuv (relative/education/...) haqiqatan ham shu employee_id'ga tegishli
    ekanini tekshiradi — aks holda 404. Boshqa xodimning yozuvini id orqali taxmin qilib
    o'zgartirishning (IDOR) oldini oladi."""
    obj = await db.get(model, item_id)
    if obj is None or obj.employee_id != employee_id:  # type: ignore[attr-defined]
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Yozuv topilmadi")
    return obj


@router.get("", response_model=list[EmployeeListItem])
async def list_employees(db: DbSession, current_user: CurrentUser, skip: int = 0, limit: int = 100) -> list[Employee]:
    return await employee_crud.list(db, skip=skip, limit=limit)


@router.post("", response_model=EmployeeDetailRead, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate, request: Request, db: DbSession, current_user: EditorUser
) -> Employee:
    if payload.pinfl and await employee_crud.get_by_pinfl(db, payload.pinfl):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Shu PINFL bilan xodim allaqachon mavjud")

    employee = await employee_crud.create(db, obj_in=payload)
    await record_audit(
        db,
        user_id=current_user.id,
        action="create",
        table_name="employees",
        record_id=employee.id,
        new_values=model_snapshot(employee),
        ip_address=client_ip(request),
    )
    await db.commit()
    return await _get_detail_or_500(db, employee.id)


@router.get("/{employee_id}", response_model=EmployeeDetailRead)
async def get_employee(employee_id: int, db: DbSession, current_user: CurrentUser) -> Employee:
    employee = await employee_crud.get_detail(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Xodim topilmadi")
    return employee


@router.patch("/{employee_id}", response_model=EmployeeDetailRead)
async def update_employee(
    employee_id: int, payload: EmployeeUpdate, request: Request, db: DbSession, current_user: EditorUser
) -> Employee:
    employee = await _get_employee_or_404(db, employee_id)
    before = model_snapshot(employee)
    employee = await employee_crud.update(db, db_obj=employee, obj_in=payload)
    await record_audit(
        db,
        user_id=current_user.id,
        action="update",
        table_name="employees",
        record_id=employee.id,
        old_values=before,
        new_values=model_snapshot(employee),
        ip_address=client_ip(request),
    )
    await db.commit()
    return await _get_detail_or_500(db, employee.id)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: int, request: Request, db: DbSession, current_user: AdminUser) -> None:
    employee = await _get_employee_or_404(db, employee_id)
    before = model_snapshot(employee)
    await employee_crud.soft_delete(db, db_obj=employee)
    await record_audit(
        db,
        user_id=current_user.id,
        action="delete",
        table_name="employees",
        record_id=employee.id,
        old_values=before,
        ip_address=client_ip(request),
    )
    await db.commit()


@router.get("/{employee_id}/sensitive", response_model=EmployeeSensitiveRead)
async def get_employee_sensitive_data(
    employee_id: int, request: Request, db: DbSession, current_user: EditorUser
) -> EmployeeSensitiveRead:
    """PINFL/pasport raqamining deshifrlangan qiymati. Har chaqiriq audit-logga
    'view_sensitive' sifatida yoziladi — kim, qachon ochganini kuzatish uchun."""
    employee = await _get_employee_or_404(db, employee_id)
    await record_audit(
        db,
        user_id=current_user.id,
        action="view_sensitive",
        table_name="employees",
        record_id=employee.id,
        ip_address=client_ip(request),
    )
    await db.commit()
    return EmployeeSensitiveRead(
        pinfl=decrypt_field(employee.pinfl_encrypted) if employee.pinfl_encrypted else None,
        passport_number=(
            decrypt_field(employee.passport_number_encrypted) if employee.passport_number_encrypted else None
        ),
    )


# Quyidagi bola-resurslar (relatives/education/work_history/awards/foreign_trips) uchun
# CRUD yuqoridagi bir xil naqsh bo'yicha takrorlanadi. Soddalik uchun bu yerda alohida
# audit-log yozilmaydi (faqat employees jadvalining o'zi audit qilinadi) — agar kerak
# bo'lsa, xuddi shu record_audit(...) chaqiruvi shu yerga ham qo'shiladi.


# ---- Yaqin qarindoshlar ----


@router.post("/{employee_id}/relatives", response_model=RelativeRead, status_code=status.HTTP_201_CREATED)
async def add_relative(
    employee_id: int, payload: RelativeCreate, db: DbSession, current_user: EditorUser
) -> Relative:
    await _get_employee_or_404(db, employee_id)
    relative = await relative_crud.create(db, obj_in={**payload.model_dump(), "employee_id": employee_id})
    await db.commit()
    return relative


@router.patch("/{employee_id}/relatives/{relative_id}", response_model=RelativeRead)
async def update_relative(
    employee_id: int, relative_id: int, payload: RelativeUpdate, db: DbSession, current_user: EditorUser
) -> Relative:
    relative = await _get_owned_or_404(db, Relative, relative_id, employee_id)
    relative = await relative_crud.update(db, db_obj=relative, obj_in=payload.model_dump(exclude_unset=True))
    await db.commit()
    return relative


@router.delete("/{employee_id}/relatives/{relative_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relative(employee_id: int, relative_id: int, db: DbSession, current_user: EditorUser) -> None:
    relative = await _get_owned_or_404(db, Relative, relative_id, employee_id)
    await relative_crud.remove(db, db_obj=relative)
    await db.commit()


# ---- Ta'lim tarixi ----


@router.post(
    "/{employee_id}/education", response_model=EducationHistoryRead, status_code=status.HTTP_201_CREATED
)
async def add_education(
    employee_id: int, payload: EducationHistoryCreate, db: DbSession, current_user: EditorUser
) -> EducationHistory:
    await _get_employee_or_404(db, employee_id)
    record = await education_history_crud.create(db, obj_in={**payload.model_dump(), "employee_id": employee_id})
    await db.commit()
    return record


@router.patch("/{employee_id}/education/{education_id}", response_model=EducationHistoryRead)
async def update_education(
    employee_id: int,
    education_id: int,
    payload: EducationHistoryUpdate,
    db: DbSession,
    current_user: EditorUser,
) -> EducationHistory:
    record = await _get_owned_or_404(db, EducationHistory, education_id, employee_id)
    record = await education_history_crud.update(db, db_obj=record, obj_in=payload.model_dump(exclude_unset=True))
    await db.commit()
    return record


@router.delete("/{employee_id}/education/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(employee_id: int, education_id: int, db: DbSession, current_user: EditorUser) -> None:
    record = await _get_owned_or_404(db, EducationHistory, education_id, employee_id)
    await education_history_crud.remove(db, db_obj=record)
    await db.commit()


# ---- Mehnat faoliyati tarixi ----


@router.post("/{employee_id}/work-history", response_model=WorkHistoryRead, status_code=status.HTTP_201_CREATED)
async def add_work_history(
    employee_id: int, payload: WorkHistoryCreate, db: DbSession, current_user: EditorUser
) -> WorkHistory:
    await _get_employee_or_404(db, employee_id)
    record = await work_history_crud.create(db, obj_in={**payload.model_dump(), "employee_id": employee_id})
    await db.commit()
    return record


@router.patch("/{employee_id}/work-history/{work_history_id}", response_model=WorkHistoryRead)
async def update_work_history(
    employee_id: int,
    work_history_id: int,
    payload: WorkHistoryUpdate,
    db: DbSession,
    current_user: EditorUser,
) -> WorkHistory:
    record = await _get_owned_or_404(db, WorkHistory, work_history_id, employee_id)
    record = await work_history_crud.update(db, db_obj=record, obj_in=payload.model_dump(exclude_unset=True))
    await db.commit()
    return record


@router.delete("/{employee_id}/work-history/{work_history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_history(
    employee_id: int, work_history_id: int, db: DbSession, current_user: EditorUser
) -> None:
    record = await _get_owned_or_404(db, WorkHistory, work_history_id, employee_id)
    await work_history_crud.remove(db, db_obj=record)
    await db.commit()


# ---- Mukofotlar ----


@router.post("/{employee_id}/awards", response_model=AwardRead, status_code=status.HTTP_201_CREATED)
async def add_award(employee_id: int, payload: AwardCreate, db: DbSession, current_user: EditorUser) -> Award:
    await _get_employee_or_404(db, employee_id)
    record = await award_crud.create(db, obj_in={**payload.model_dump(), "employee_id": employee_id})
    await db.commit()
    return record


@router.patch("/{employee_id}/awards/{award_id}", response_model=AwardRead)
async def update_award(
    employee_id: int, award_id: int, payload: AwardUpdate, db: DbSession, current_user: EditorUser
) -> Award:
    record = await _get_owned_or_404(db, Award, award_id, employee_id)
    record = await award_crud.update(db, db_obj=record, obj_in=payload.model_dump(exclude_unset=True))
    await db.commit()
    return record


@router.delete("/{employee_id}/awards/{award_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_award(employee_id: int, award_id: int, db: DbSession, current_user: EditorUser) -> None:
    record = await _get_owned_or_404(db, Award, award_id, employee_id)
    await award_crud.remove(db, db_obj=record)
    await db.commit()


# ---- Xorijga chiqishlar ----


@router.post(
    "/{employee_id}/foreign-trips", response_model=ForeignTripRead, status_code=status.HTTP_201_CREATED
)
async def add_foreign_trip(
    employee_id: int, payload: ForeignTripCreate, db: DbSession, current_user: EditorUser
) -> ForeignTrip:
    await _get_employee_or_404(db, employee_id)
    record = await foreign_trip_crud.create(db, obj_in={**payload.model_dump(), "employee_id": employee_id})
    await db.commit()
    return record


@router.patch("/{employee_id}/foreign-trips/{trip_id}", response_model=ForeignTripRead)
async def update_foreign_trip(
    employee_id: int, trip_id: int, payload: ForeignTripUpdate, db: DbSession, current_user: EditorUser
) -> ForeignTrip:
    record = await _get_owned_or_404(db, ForeignTrip, trip_id, employee_id)
    record = await foreign_trip_crud.update(db, db_obj=record, obj_in=payload.model_dump(exclude_unset=True))
    await db.commit()
    return record


@router.delete("/{employee_id}/foreign-trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_foreign_trip(employee_id: int, trip_id: int, db: DbSession, current_user: EditorUser) -> None:
    record = await _get_owned_or_404(db, ForeignTrip, trip_id, employee_id)
    await foreign_trip_crud.remove(db, db_obj=record)
    await db.commit()


# ---- Biriktirilgan hujjatlar (diplom, pasport skani, fotosurat va h.k.) ----
# Ro'yxat uchun alohida GET yo'q — boshqa bola-resurslar kabi EmployeeDetailRead'ning
# o'zida keladi (crud/employee.py'dagi _DETAIL_RELATIONSHIPS). Faqat yozish/yuklab olish
# amallari (JSON emas, fayl oqimi) shu yerda alohida endpoint sifatida beriladi.


@router.post(
    "/{employee_id}/attachments", response_model=DocumentAttachmentRead, status_code=status.HTTP_201_CREATED
)
async def upload_attachment(
    employee_id: int,
    request: Request,
    db: DbSession,
    current_user: EditorUser,
    file: Annotated[UploadFile, File()],
    file_type: Annotated[str, Form()],
) -> DocumentAttachment:
    await _get_employee_or_404(db, employee_id)

    try:
        relative_path, size_bytes, content_type = await save_attachment(employee_id, file)
    except UploadValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None

    attachment = await document_attachment_crud.create(
        db,
        obj_in={
            "employee_id": employee_id,
            "file_type": file_type.strip()[:50] or "boshqa",
            "original_filename": (file.filename or "fayl")[:255],
            "stored_path": relative_path,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "uploaded_by_id": current_user.id,
        },
    )
    await record_audit(
        db,
        user_id=current_user.id,
        action="upload_document",
        table_name="document_attachments",
        record_id=attachment.id,
        new_values={"original_filename": attachment.original_filename, "file_type": attachment.file_type},
        ip_address=client_ip(request),
    )
    await db.commit()
    return attachment


@router.get("/{employee_id}/attachments/{attachment_id}/download")
async def download_attachment(
    employee_id: int, attachment_id: int, request: Request, db: DbSession, current_user: CurrentUser
) -> FileResponse:
    attachment = await _get_owned_or_404(db, DocumentAttachment, attachment_id, employee_id)
    path = resolve_stored_path(attachment.stored_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fayl serverda topilmadi")

    await record_audit(
        db,
        user_id=current_user.id,
        action="download_document",
        table_name="document_attachments",
        record_id=attachment.id,
        ip_address=client_ip(request),
    )
    await db.commit()

    safe_name = "".join(c for c in attachment.original_filename if c.isalnum() or c in " ._-").strip() or "fayl"
    return FileResponse(path, media_type=attachment.content_type, filename=safe_name)


@router.delete("/{employee_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    employee_id: int, attachment_id: int, request: Request, db: DbSession, current_user: EditorUser
) -> None:
    attachment = await _get_owned_or_404(db, DocumentAttachment, attachment_id, employee_id)
    stored_path = attachment.stored_path

    await record_audit(
        db,
        user_id=current_user.id,
        action="delete_document",
        table_name="document_attachments",
        record_id=attachment.id,
        old_values={"original_filename": attachment.original_filename, "file_type": attachment.file_type},
        ip_address=client_ip(request),
    )
    await document_attachment_crud.remove(db, db_obj=attachment)
    await db.commit()

    # DB yozuvi commit qilingandan KEYIN faylni o'chiramiz — aks holda fayl o'chib, DB
    # yozuvi qolib ketsa, keyingi yuklab olish urinishi "topilmadi" bilan buziladi;
    # teskari tartibda eng yomon holat faqat egasiz fayl qoldirish (zararsiz).
    await delete_attachment_file(stored_path)
