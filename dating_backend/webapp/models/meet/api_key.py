from uuid import uuid4, UUID as Uuid

from sqlalchemy import Integer, UUID
from sqlalchemy.orm import Mapped, mapped_column

from webapp.models.meta import Base


class ApiKey(Base):
    __tablename__ = 'api_key'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    key: Mapped[Uuid] = mapped_column(UUID, default=uuid4)
