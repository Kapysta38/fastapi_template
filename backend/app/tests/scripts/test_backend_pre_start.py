from unittest.mock import MagicMock, patch, ANY
from sqlalchemy import select

from app.backend_pre_start import init, logger


def test_init_successful_connection() -> None:
    engine_mock = MagicMock()

    session_mock = MagicMock()
    session_mock.execute.return_value = True

    session_class_mock = MagicMock()
    session_class_mock.return_value.__enter__.return_value = session_mock
    session_class_mock.return_value.__exit__.return_value = None

    with (
        patch("app.backend_pre_start.Session", session_class_mock),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            init(engine_mock)
            connection_successful = True
        except Exception:
            connection_successful = False

        assert connection_successful, "Connection should succeed"
        session_mock.execute.assert_called_once_with(ANY)
