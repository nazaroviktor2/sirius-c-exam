from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

from webapp.models.meet.form import GenderEnum


class FormCreate(BaseModel):
    name: str
    gender: GenderEnum
    age: int
    height: Optional[float] = None
    description: Optional[str] = None
    city_name: Optional[str] = None
    city_point: Optional[str] = None
    is_active: bool = True


class FormResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    name: str
    gender: GenderEnum
    age: int
    height: Optional[float]
    description: Optional[str]
    city_name: Optional[str]
    is_active: bool
    created_at: datetime


class FormUpdate(BaseModel):
    gender: Optional[GenderEnum] = None
    name: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    city_name: Optional[str] = None
    city_point: Optional[str] = None
