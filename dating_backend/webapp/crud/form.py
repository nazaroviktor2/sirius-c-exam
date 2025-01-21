from datetime import timedelta
from typing import Optional, List, Sequence, Any

from sqlalchemy import select, exists, func, not_, case, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql.operators import and_, or_, is_

from webapp.cache.redis.rate_limit import rate_limit
from webapp.models.meet.form import Form
from webapp.models.meet.search_params import SearchParams
from webapp.schema.form.form import FormCreate, FormUpdate
from webapp.logger import logger


async def get_user_form(session: AsyncSession, user_id: int) -> Optional[Form]:
    return (
        await session.scalars(
            select(Form).where(
                Form.user_id == user_id,
            )
        )
    ).one_or_none()


async def get_form(session: AsyncSession, form_id: int) -> Optional[Form]:
    return (
        await session.scalars(
            select(Form).where(
                Form.id == form_id,
            )
        )
    ).one_or_none()


async def check_user_from_exists(session: AsyncSession, user_id: int) -> bool:
    query = select(exists().where(
        Form.user_id == user_id
    ))
    return bool(await session.scalar(query))


async def create_form(
    session: AsyncSession, user_id: int,
    form_info: FormCreate
) -> Optional[Form]:
    try:
        new_form = Form(**form_info.model_dump())
        new_form.user_id = user_id

        session.add(new_form)
        await session.commit()

        return new_form
    except Exception as err:
        logger.error(f'An error occurred while creating the profile: {err}')
        await session.rollback()
        return None


async def update_form(session: AsyncSession, form: Form, updated_info: FormUpdate) -> Optional[Form]:
    try:
        for key, value in updated_info.model_dump(exclude_unset=True).items():
            setattr(form, key, value)
        await session.commit()
        return form
    except Exception as err:
        logger.error(f'An error occurred while updating the profile: {err}')
        await session.rollback()
        raise None


@rate_limit(max_calls=3, period=timedelta(days=1))
async def get_forms_by_search_params(
        session: AsyncSession,
        shown_ids: Optional[List[int]] = None,
        limit: Optional[int] = 100,
        user_id: int = None
) -> Optional[Sequence[Row | RowMapping | Any]]:
    search_form = aliased(Form, name='sf')
    sf_params = aliased(SearchParams, name='sf_sp')

    user_form = aliased(Form, name='uf')
    uf_params = aliased(SearchParams, name='uf_sp')

    if not shown_ids:
        shown_ids = list()

    query = (
        select(search_form.id)
        .where(
            search_form.user_id != user_form.user_id,
            search_form.is_active.is_(True),
            not_(search_form.id.in_(shown_ids))
        )
        .join(sf_params, sf_params.user_id == search_form.user_id)
        .join(user_form, user_form.user_id == user_id)
        .join(uf_params, uf_params.user_id == user_form.user_id)
        .filter(
            or_(uf_params.gender.is_(None), uf_params.gender == search_form.gender),
            or_(uf_params.min_age.is_(None), uf_params.min_age <= search_form.age),
            or_(uf_params.max_age.is_(None), uf_params.max_age >= search_form.age),
            or_(uf_params.min_height.is_(None), uf_params.min_height <= search_form.height),
            or_(uf_params.max_height.is_(None), uf_params.max_height >= search_form.age),
            or_(uf_params.city_point.is_(None), func.ST_Distance(uf_params.city_point, search_form.city_point) <= 2)
        )
        .filter(
            or_(sf_params.gender.is_(None), sf_params.gender == user_form.gender),
            or_(sf_params.min_age.is_(None), sf_params.min_age <= user_form.age),
            or_(sf_params.max_age.is_(None), sf_params.max_age >= user_form.age),
            or_(sf_params.min_height.is_(None), sf_params.min_height <= user_form.height),
            or_(sf_params.max_height.is_(None), sf_params.max_height >= user_form.height),
            or_(sf_params.city_point.is_(None), func.ST_Distance(sf_params.city_point, user_form.city_point) <= 2)
        ).limit(limit)
    )

    result = (await session.scalars(query)).all()
    if not result:
        return None

    return result
