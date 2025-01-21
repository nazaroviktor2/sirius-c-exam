from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import Base, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from webapp.models.meet.user import User


class Statistics(Base):
    __tablename__ = 'statistics'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(f'{DEFAULT_SCHEMA}.user.id', ondelete='CASCADE'), nullable=False
    )

    user: Mapped['User'] = relationship('User', foreign_keys=[user_id])

    likes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    matches: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
