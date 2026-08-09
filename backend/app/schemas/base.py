from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    """SQLAlchemy modellaridan to'g'ridan-to'g'ri o'qiladigan (from_attributes) javob sxemalari uchun asos."""

    model_config = ConfigDict(from_attributes=True)
