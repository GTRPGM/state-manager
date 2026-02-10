"""Proxy router tests - 프록시 헬스체크 엔드포인트 테스트"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_proxy_health_check_all_connected(async_client: AsyncClient):
    """모든 서비스가 연결된 경우 헬스체크 테스트"""
    with (
        patch(
            "state_db.proxy.services.RuleEngineProxy.health_check",
            new=AsyncMock(return_value={"status": "ok"}),
        ),
        patch(
            "state_db.proxy.services.GMProxy.health_check",
            new=AsyncMock(return_value={"status": "ok"}),
        ),
    ):
        response = await async_client.get("/state/health/proxy")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "healthy"
        assert data["data"]["services"]["rule_engine"] == "connected"
        assert data["data"]["services"]["gm"] == "connected"


@pytest.mark.asyncio
async def test_proxy_health_check_partial_failure(async_client: AsyncClient):
    """일부 서비스 연결 실패 시 degraded 상태 테스트"""
    with (
        patch(
            "state_db.proxy.services.RuleEngineProxy.health_check",
            new=AsyncMock(return_value={"status": "ok"}),
        ),
        patch(
            "state_db.proxy.services.GMProxy.health_check",
            new=AsyncMock(side_effect=ConnectionError("Connection refused")),
        ),
    ):
        response = await async_client.get("/state/health/proxy")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "degraded"
        assert data["data"]["services"]["rule_engine"] == "connected"
        assert "disconnected" in data["data"]["services"]["gm"]


@pytest.mark.asyncio
async def test_proxy_health_check_all_disconnected(async_client: AsyncClient):
    """모든 서비스 연결 실패 시 테스트"""
    with (
        patch(
            "state_db.proxy.services.RuleEngineProxy.health_check",
            new=AsyncMock(side_effect=ConnectionError("Connection refused")),
        ),
        patch(
            "state_db.proxy.services.GMProxy.health_check",
            new=AsyncMock(side_effect=TimeoutError("Timeout")),
        ),
    ):
        response = await async_client.get("/state/health/proxy")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "degraded"
        assert "disconnected" in data["data"]["services"]["rule_engine"]
        assert "disconnected" in data["data"]["services"]["gm"]


@pytest.mark.asyncio
async def test_rule_engine_health_connected(async_client: AsyncClient):
    """Rule Engine 개별 헬스체크 - 연결 성공"""
    with patch(
        "state_db.proxy.services.RuleEngineProxy.health_check",
        new=AsyncMock(return_value={"status": "ok", "version": "1.0.0"}),
    ):
        response = await async_client.get("/state/health/proxy/rule-engine")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["connected"] is True
        assert data["data"]["response"]["status"] == "ok"


@pytest.mark.asyncio
async def test_rule_engine_health_disconnected(async_client: AsyncClient):
    """Rule Engine 개별 헬스체크 - 연결 실패"""
    with patch(
        "state_db.proxy.services.RuleEngineProxy.health_check",
        new=AsyncMock(side_effect=ConnectionError("Connection refused")),
    ):
        response = await async_client.get("/state/health/proxy/rule-engine")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["connected"] is False
        assert "error" in data["data"]


@pytest.mark.asyncio
async def test_gm_health_connected(async_client: AsyncClient):
    """GM 개별 헬스체크 - 연결 성공"""
    with patch(
        "state_db.proxy.services.GMProxy.health_check",
        new=AsyncMock(return_value={"status": "ok", "model": "gpt-4"}),
    ):
        response = await async_client.get("/state/health/proxy/gm")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["connected"] is True


@pytest.mark.asyncio
async def test_gm_health_disconnected(async_client: AsyncClient):
    """GM 개별 헬스체크 - 연결 실패"""
    with patch(
        "state_db.proxy.services.GMProxy.health_check",
        new=AsyncMock(side_effect=TimeoutError("Request timeout")),
    ):
        response = await async_client.get("/state/health/proxy/gm")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["connected"] is False
        assert "error" in data["data"]
