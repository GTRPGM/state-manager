import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(async_client: AsyncClient):
    """루트 엔드포인트 테스트"""
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "data": {
            "message": "반갑습니다. GTRPGM 상태 관리자입니다!",
            "service": "State Manager",
            "version": "1.0.0",
        },
    }


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """헬스체크 엔드포인트 테스트"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
