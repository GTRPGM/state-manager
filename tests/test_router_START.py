from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

# Mock data
MOCK_SESSION_ID = "test-session-id"
MOCK_PLAYER_ID = "test-player-id"
MOCK_SCENARIO_ID = "550e8400-e29b-41d4-a716-446655440000"


@pytest.mark.asyncio
async def test_start_session(async_client: AsyncClient):
    mock_response = {
        "session_id": MOCK_SESSION_ID,
        "scenario_id": MOCK_SCENARIO_ID,
        "player_id": MOCK_PLAYER_ID,
        "current_act": 1,
        "current_sequence": 1,
        "location": "Starting Town",
        "status": "active",
    }

    with patch(
        "state_db.repositories.SessionRepository.start",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.post(
            "/state/session/start",
            json={
                "scenario_id": MOCK_SCENARIO_ID,
                "current_act": 1,
                "current_sequence": 1,
                "location": "Starting Town",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["session_id"] == MOCK_SESSION_ID
