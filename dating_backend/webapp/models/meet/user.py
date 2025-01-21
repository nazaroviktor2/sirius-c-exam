from enum import Enum
from datetime import datetime

from sqlalchemy import BigInteger, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from webapp.models.meta import Base


class UserRoleEnum(Enum):
    admin = 'admin'
    user = 'user'


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    role: Mapped[UserRoleEnum] = mapped_column(ENUM(UserRoleEnum, inherit_schema=True), default=UserRoleEnum.user)

    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
