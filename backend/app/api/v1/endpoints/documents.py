from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.api.v1.deps import CurrentUser, DbSession, client_ip
from app.crud.employee import employee_crud
from app.services.audit_service import record_audit
from app.services.docx_generator import generate_objektivka

router = APIRouter()


@router.get("/employees/{employee_id}/objektivka")
async def download_objektivka(employee_id: int, request: Request, db: DbSession, current_user: CurrentUser):
    employee = await employee_crud.get_detail(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Xodim topilmadi")

    buffer = generate_objektivka(employee)

    await record_audit(
        db,
        user_id=current_user.id,
        action="generate_document",
        table_name="employees",
        record_id=employee.id,
        ip_address=client_ip(request),
    )
    await db.commit()

    # Fayl nomi xodim F.I.Sh'idan yasaladi; foydalanuvchi ma'lumotlari to'g'ridan-to'g'ri HTTP
    # header'ga qo'yilishining oldini olish uchun faqat harf/raqam/bo'shliqqa cheklab tozalanadi
    # (aks holda maxsus belgilar orqali header injection xavfi bo'lardi).
    safe_name = "".join(c for c in employee.full_name if c.isalnum() or c in " _-").strip() or "obyektivka"
    filename = f"{safe_name}.docx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
