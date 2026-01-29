import os

import pytest
from httpx import ASGITransport, AsyncClient
from testcontainers.postgres import PostgresContainer

from state_db.infrastructure import shutdown, startup
from state_db.main import app

# 테스트 환경 변수 설정
os.environ["APP_ENV"] = "test"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def postgres_container():
    """
    postgres-ex 이미지를 사용하여 임시 컨테이너를 띄웁니다.
    세션 전체에서 하나만 유지하여 성능 최적화.
    """
    with PostgresContainer("postgres-ex", port=5432) as postgres:
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
    """
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
