from app.schemas.base import ORMBase


class RoleRead(ORMBase):
    id: int
    code: str
    display_name: str
