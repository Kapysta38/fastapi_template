import pytest

from app.db.session import engine
from app.backend_pre_start import init


async def test_database_connection():
    try:
        await init(engine)
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")
