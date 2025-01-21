import json
import asyncio
import argparse
import logging
from pathlib import Path
from typing import List

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from webapp.db.postgres import async_session
from webapp.models.meta import metadata

parser = argparse.ArgumentParser()

parser.add_argument('fixtures', nargs='+', help='<Required> Set flag')

args = parser.parse_args()


async def main(fixtures: List[str]) -> None:
    for fixture in fixtures:
        fixture_path = Path(fixture)
        model = metadata.tables[fixture_path.stem]

        with open(fixture_path, 'r') as file:
            values = json.load(file)
        try:
            async with async_session() as session:
                await session.execute(insert(model).values(values))
                await session.commit()
        except IntegrityError:
            await session.rollback()
            logging.error(f'Already exists: {fixture_path}')


if __name__ == '__main__':
    asyncio.run(main(args.fixtures))
