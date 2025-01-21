from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import BigInteger, Integer, ForeignKey, Float, String, Column
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meet.form import GenderEnum
from webapp.models.meta import Base, DEFAULT_SCHEMA

if TYPE_CHECKING:
    from webapp.models.meet.user import User


class SearchParams(Base):
    __tablename__ = 'search_params'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    gender: Mapped[GenderEnum] = mapped_column(ENUM(GenderEnum, inherit_schema=True), nullable=True)

    min_age: Mapped[int] = mapped_column(Integer, nullable=True, default=None)

    max_age: Mapped[int] = mapped_column(Integer, nullable=True, default=None)

    min_height: Mapped[float] = mapped_column(Float, nullable=True, default=None)

    max_height: Mapped[float] = mapped_column(Float, nullable=True, default=None)

    city_name: Mapped[str] = mapped_column(String, nullable=True, default=None)

    city_point = Column(Geometry('POINT'), nullable=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(f'{DEFAULT_SCHEMA}.user.id'), nullable=False
    )

    user: Mapped['User'] = relationship('User', foreign_keys=[user_id])
