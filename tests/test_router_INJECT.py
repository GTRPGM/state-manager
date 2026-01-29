from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_inject_scenario(async_client: AsyncClient):
    mock_scenario_id = "test-scenario-uuid"
    mock_response_data = {
        "scenario_id": mock_scenario_id,
        "title": "Test Scenario",
        "status": "success",
        "message": "Scenario and master entities injected successfully",
    }

    with patch(
        "state_db.repositories.scenario.ScenarioRepository.inject_scenario",
        new=AsyncMock(return_value=mock_response_data),
    ):
        inject_data = {
            "title": "Test Scenario",
            "description": "A test scenario",
            "npcs": [
                {
                    "scenario_npc_id": "npc-1",
                    "name": "Test NPC",
                    "description": "A test NPC",
                }
            ],
            "enemies": [
                {
                    "scenario_enemy_id": "enemy-1",
                    "name": "Test Enemy",
                    "description": "A test Enemy",
                }
            ],
            "items": [
                {
                    "item_id": "550e8400-e29b-41d4-a716-446655440001",
                    "name": "Test Item",
                    "description": "A test Item",
                }
            ],
        }

        response = await async_client.post(
            "/state/scenario/inject",
            json=inject_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["scenario_id"] == mock_scenario_id
        assert data["data"]["title"] == "Test Scenario"
