from fastapi import APIRouter

from app.api.v1.endpoints import auth, departments, documents, employees, reports, search, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
api_router.include_router(departments.router, tags=["departments"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(documents.router, tags=["documents"])
api_router.include_router(reports.router, tags=["reports"])
