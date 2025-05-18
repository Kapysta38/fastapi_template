import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    before_log,
    after_log,
)
from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init(db_engine: AsyncEngine) -> None:
    async_session = async_sessionmaker(bind=db_engine, expire_on_commit=False)

    async with async_session() as session:
        await session.execute(select(1))


async def main() -> None:
    logger.info("Initializing service")
    await init(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
