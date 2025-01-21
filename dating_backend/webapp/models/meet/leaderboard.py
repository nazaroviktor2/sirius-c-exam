from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, Integer, String, select, desc, func, event, Select, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils.view import DropView, CreateView

from webapp.logger import logger
from webapp.models.meet.form import Form
from webapp.models.meet.statistics import Statistics
from webapp.models.meta import DEFAULT_SCHEMA, Base

Base_ = declarative_base(metadata=MetaData())


class Leaderboard(Base_):
    __tablename__ = f'{DEFAULT_SCHEMA}.leaderboard'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    rank: Mapped[int] = mapped_column(Integer)
    likes: Mapped[int] = mapped_column(Integer)

    selectable: Select = (select(
        Statistics.user_id.label('user_id'),
        Form.name.label('name'),
        Statistics.likes.label('likes'),
        func.row_number().over(order_by=desc(Statistics.likes)).label('rank')
    ).join(Form, Statistics.user_id == Form.user_id)).group_by(
        Statistics.user_id, Statistics.likes, Form.name
    )


event.listen(
    Base.metadata,
    "after_create",
    CreateView(
        Leaderboard.__tablename__,
        Leaderboard.selectable,
        materialized=True
    )
)

event.listen(
    Base.metadata,
    'before_drop',
    DropView(
        Leaderboard.__tablename__,
        materialized=True
    )
)
