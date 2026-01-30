from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from state_db.schemas.scenario import ScenarioInjectResponse


@pytest.mark.asyncio
async def test_inject_scenario(async_client: AsyncClient):
    mock_scenario_id = "test-scenario-uuid"
    mock_response = ScenarioInjectResponse(
        scenario_id=mock_scenario_id,
        title="Test Scenario",
        status="success",
        message="Scenario structure injected successfully",
    )

    with patch(
        "state_db.repositories.scenario.ScenarioRepository.inject_scenario",
        new=AsyncMock(return_value=mock_response),
    ):
        inject_data = {
            "title": "Test Scenario",
            "data": {
                "title": "Test Scenario",
                "description": "A test scenario",
                "acts": [{"id": "act-1", "name": "Act 1"}],
                "sequences": [
                    {"id": "seq-1", "name": "Seq 1", "location_name": "Room"}
                ],
                "npcs": [],
                "enemies": [],
                "items": [],
            },
        }

        response = await async_client.post(
            "/state/scenario/inject",
            json=inject_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["scenario_id"] == mock_scenario_id
