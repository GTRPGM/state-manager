import os
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from state_db.main import app

# 테스트 환경 변수 설정
os.environ["APP_ENV"] = "test"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_db_pool():
    """
    DatabaseManager의 커넥션 풀을 Mocking합니다.
    실제 DB에 연결하지 않고 쿼리 실행을 흉내냅니다.
    """
    # Mock Connection 객체 생성
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = []
    mock_conn.fetchrow.return_value = None
    mock_conn.execute.return_value = "COMMAND OK"

    # 트랜잭션/커넥션 컨텍스트 매니저 지원
    mock_conn.__aenter__.return_value = mock_conn
    mock_conn.__aexit__.return_value = None

    # Pool Acquire 컨텍스트 매니저 지원
    mock_pool = AsyncMock()
    mock_pool.acquire.return_value = mock_conn

    # DatabaseManager.get_pool()이 이 mock_pool을 반환하도록 설정
    with (
        patch(
            "state_db.infrastructure.database.DatabaseManager.get_pool",
            new=AsyncMock(return_value=mock_pool),
        ),
        patch(
            "state_db.infrastructure.database.DatabaseManager.get_connection"
        ) as mock_get_conn,
    ):
        # get_connection 자체가 컨텍스트 매니저임
        mock_get_conn.return_value.__aenter__.return_value = mock_conn
        mock_get_conn.return_value.__aexit__.return_value = None

        yield mock_conn


@pytest.fixture
async def async_client(mock_db_pool) -> AsyncGenerator[AsyncClient, None]:
    """
    FastAPI 앱 테스트를 위한 비동기 클라이언트
    """
    # DB startup/shutdown 이벤트 무력화 (Mock 사용하므로)
    with (
        patch("state_db.infrastructure.startup", new=AsyncMock()),
        patch("state_db.infrastructure.shutdown", new=AsyncMock()),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client
