from pydantic import BaseModel, ConfigDict
from datetime import datetime

from webapp.models.meet.user import UserRoleEnum


class UserLogin(BaseModel):
    id: int


class UserLoginResponse(BaseModel):
    access_token: str
    role: str


class UserInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: UserRoleEnum
    is_banned: bool
    created_at: datetime
