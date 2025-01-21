from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import Base, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from webapp.models.meet.user import User


class ContentEnum(str, Enum):
    photo = 'image/jpeg'
    video = 'video/mp4'


class Image(Base):
    __tablename__ = 'image'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(f'{DEFAULT_SCHEMA}.user.id', ondelete='CASCADE'), nullable=False
    )

    user: Mapped['User'] = relationship('User', foreign_keys=[user_id])

    path: Mapped[str] = mapped_column(Text, nullable=False)

    content_type: Mapped[ContentEnum] = mapped_column(ENUM(ContentEnum, inherit_schema=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
