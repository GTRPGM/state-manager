from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from state_db.schemas.scenario import ScenarioInjectResponse


@pytest.mark.asyncio
async def test_scenario_list(async_client: AsyncClient):
    """시나리오 목록 조회 API 테스트"""
    repo_path = "state_db.repositories.scenario.ScenarioRepository.get_all_scenarios"
    with patch(
        repo_path,
        new=AsyncMock(return_value=[]),
    ):
        response = await async_client.get("/state/scenario/list")
        assert response.status_code == 200
        assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_scenario_validate_success(async_client: AsyncClient):
    """시나리오 검증 API 성공 케이스"""
    valid_data = {
        "title": "Valid Scenario",
        "description": "Desc",
        "acts": [],
        "sequences": [],
        "npcs": [
            {
                "scenario_npc_id": "npc-1",
                "name": "NPC 1",
                "description": "Desc",
                "tags": [],
                "state": {},
            }
        ],
        "enemies": [],
        "items": [],
        "relations": [],
    }
    response = await async_client.post("/state/scenario/validate", json=valid_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["is_valid"] is True


@pytest.mark.asyncio
async def test_scenario_validate_fail(async_client: AsyncClient):
    """시나리오 검증 API 실패 케이스 (비정상 데이터)"""
    # 필수 필드 누락 등 (Pydantic 수준 검증)
    invalid_data = {
        "title": "Invalid"
        # npcs, acts 등 필수 리스트 누락
    }
    response = await async_client.post("/state/scenario/validate", json=invalid_data)
    assert response.status_code == 422  # Validation Error


@pytest.mark.asyncio
async def test_scenario_inject(async_client: AsyncClient):
    """시나리오 주입 API 테스트 (모킹)"""
    mock_scenario_id = "test-uuid"
    mock_response = ScenarioInjectResponse(
        scenario_id=mock_scenario_id,
        title="Test Scenario",
        status="success",
        message="Scenario structure injected successfully",
    )

    repo_path = "state_db.repositories.scenario.ScenarioRepository.inject_scenario"
    with patch(
        repo_path,
        new=AsyncMock(return_value=mock_response),
    ):
        inject_data = {
            "title": "Test Scenario",
            "description": "Desc",
            "acts": [],
            "sequences": [],
            "npcs": [],
            "enemies": [],
            "items": [],
            "relations": [],
        }
        response = await async_client.post("/state/scenario/inject", json=inject_data)
        assert response.status_code == 200
        assert response.json()["data"]["scenario_id"] == mock_scenario_id
