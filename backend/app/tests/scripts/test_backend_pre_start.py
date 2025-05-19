import pytest

from app.backend_pre_start import init
from app.db.session import engine


async def test_database_connection() -> None:
    try:
        await init(engine)
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")
