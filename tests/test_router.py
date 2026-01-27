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


@pytest.mark.asyncio
async def test_end_session(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.end", new=AsyncMock()
    ) as mock_end:
        response = await async_client.post(f"/state/session/{MOCK_SESSION_ID}/end")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        mock_end.assert_called_once_with(MOCK_SESSION_ID)


@pytest.mark.asyncio
async def test_update_player_hp(async_client: AsyncClient):
    mock_response = {
        "player_id": MOCK_PLAYER_ID,
        "name": "Test Player",
        "current_hp": 90,
        "max_hp": 100,
        "hp_change": -10,
    }

    with patch(
        "state_db.repositories.PlayerRepository.update_hp",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.put(
            f"/state/player/{MOCK_PLAYER_ID}/hp",
            json={"session_id": MOCK_SESSION_ID, "hp_change": -10, "reason": "combat"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["current_hp"] == 90


@pytest.mark.asyncio
async def test_update_inventory(async_client: AsyncClient):
    mock_response = {"player_id": MOCK_PLAYER_ID, "item_id": 5, "quantity": 3}

    with patch(
        "state_db.repositories.PlayerRepository.update_inventory",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.put(
            "/state/inventory/update",
            json={"player_id": MOCK_PLAYER_ID, "item_id": 5, "quantity": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
