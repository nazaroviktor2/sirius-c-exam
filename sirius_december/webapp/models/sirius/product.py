from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import DECIMAL, BigInteger, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from webapp.models.meta import Base

if TYPE_CHECKING:
    from webapp.models.sirius.user_product_feedback import UserProductFeedBack
    from webapp.models.sirius.order import Order


class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    offer: Mapped[str] = mapped_column(String)

    title: Mapped[str] = mapped_column(String)

    picture_url: Mapped[str] = mapped_column(Text)

    url: Mapped[str] = mapped_column(Text)

    price: Mapped[Decimal] = mapped_column(DECIMAL)

    user_product_feedbacks: Mapped[List['UserProductFeedBack']] = relationship(
        'UserProductFeedBack', back_populates='product'
    )
    orders: Mapped[List['Order']] = relationship('Order', back_populates='product')

    @hybrid_property
    def get_columns(self) -> List[str]:
        return self.__table__.columns.keys()
