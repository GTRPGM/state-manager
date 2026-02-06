import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer

from state_db.infrastructure import shutdown, startup
from state_db.main import app

# 테스트 환경 변수 설정
os.environ["APP_ENV"] = "test"


@pytest.fixture(autouse=True)
def mock_rule_engine_proxy():
    """Rule Engine 연동 자동 모킹"""
    # 통합 라우터(router_SESSION)로 패치 경로 수정
    with patch(
        "state_db.routers.router_SESSION.RuleEngineProxy.add_session",
        new_callable=AsyncMock,
    ) as mock:
        mock.return_value = {"status": "success"}
        yield mock


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def postgres_container():
    """
    postgres-ex 이미지를 사용하여 임시 컨테이너를 띄웁니다.
    세션 전체에서 하나만 유지하여 성능 최적화.
    """
    with PostgresContainer("ghcr.io/gtrpgm/postgres-ex:latest", port=5432) as postgres:
        os.environ["DB_HOST"] = postgres.get_container_host_ip()
        os.environ["DB_PORT"] = str(postgres.get_exposed_port(5432))
        os.environ["DB_USER"] = postgres.username
        os.environ["DB_PASSWORD"] = postgres.password
        os.environ["DB_NAME"] = postgres.dbname

        yield postgres


@pytest.fixture(scope="function")
async def db_lifecycle(postgres_container):
    """
    테스트 함수마다 DB 초기화 및 정리.
    CASCADE를 사용하여 이전 테스트의 잔재를 완벽히 제거.
    """
    from state_db.infrastructure import DatabaseManager

    async with DatabaseManager.get_connection() as conn:
        # Graph 정리 (AGE)
        try:
            await conn.execute("SELECT drop_graph('state_db', true);")
        except Exception:
            pass  # 그래프가 없으면 무시

        await conn.execute("""
            DROP TABLE IF EXISTS turn CASCADE;
            DROP TABLE IF EXISTS inventory CASCADE;
            DROP TABLE IF EXISTS enemy CASCADE;
            DROP TABLE IF EXISTS npc CASCADE;
            DROP TABLE IF EXISTS player CASCADE;
            DROP TABLE IF EXISTS session_snapshot CASCADE;
            DROP TABLE IF EXISTS session CASCADE;
            DROP TABLE IF EXISTS scenario_sequence CASCADE;
            DROP TABLE IF EXISTS scenario_act CASCADE;
            DROP TABLE IF EXISTS scenario CASCADE;
            DROP TABLE IF EXISTS item CASCADE;

            -- 타입 및 함수 정리 (잔재 제거)
            DROP TYPE IF EXISTS session_status CASCADE;
            DROP FUNCTION IF EXISTS initialize_enemies CASCADE;
            DROP FUNCTION IF EXISTS initialize_npcs CASCADE;
            DROP FUNCTION IF EXISTS create_session CASCADE;
        """)

    await startup()
    yield
    await shutdown()


@pytest.fixture(scope="function")
async def real_db_client(db_lifecycle) -> AsyncClient:
    """
    실제 컨테이너 DB를 사용하는 API 클라이언트.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def async_client(real_db_client: AsyncClient) -> AsyncClient:
    """
    기존 테스트와의 호환성을 위한 피스처 별칭.
    """
    return real_db_client
