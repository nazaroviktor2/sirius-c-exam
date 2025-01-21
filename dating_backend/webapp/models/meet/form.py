from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import (
    Integer, ForeignKey, DateTime, Text,
    String, Float, Boolean, BigInteger, Column
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import Base, DEFAULT_SCHEMA


if TYPE_CHECKING:
    from webapp.models.meet.user import User


class GenderEnum(str, Enum):
    male = 'male'
    female = 'female'


class Form(Base):
    __tablename__ = 'form'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    gender: Mapped[GenderEnum] = mapped_column(ENUM(GenderEnum, inherit_schema=True), nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=False)

    description: Mapped[str] = mapped_column(String, nullable=True)

    age: Mapped[int] = mapped_column(Integer, nullable=False)

    height: Mapped[float] = mapped_column(Float, nullable=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(f'{DEFAULT_SCHEMA}.user.id'), nullable=False
    )

    user: Mapped['User'] = relationship('User', foreign_keys=[user_id])

    city_name: Mapped[str] = mapped_column(String, nullable=True, default=None)

    city_point = Column(Geometry('POINT'), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
