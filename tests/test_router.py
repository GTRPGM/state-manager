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
        "current_act": 1,
        "current_sequence": 1,
        "current_phase": "exploration",
        "current_turn": 1,
        "location": "Starting Town",
        "status": "active",
        "started_at": "2026-01-25T10:00:00",
    }

    with patch(
        "state_db.router.session_start", new=AsyncMock(return_value=mock_response)
    ) as mock_session_start:
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

        mock_session_start.assert_called_once_with(
            scenario_id=MOCK_SCENARIO_ID,
            current_act=1,
            current_sequence=1,
            location="Starting Town",
        )


@pytest.mark.asyncio
async def test_end_session(async_client: AsyncClient):
    mock_response = {"status": "success", "message": f"Session {MOCK_SESSION_ID} ended"}

    with patch(
        "state_db.router.session_end", new=AsyncMock(return_value=mock_response)
    ) as mock_session_end:
        response = await async_client.post(f"/state/session/{MOCK_SESSION_ID}/end")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        mock_session_end.assert_called_once_with(MOCK_SESSION_ID)


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
        "state_db.router.update_player_hp", new=AsyncMock(return_value=mock_response)
    ) as mock_update_hp:
        response = await async_client.put(
            f"/state/player/{MOCK_PLAYER_ID}/hp",
            json={"session_id": MOCK_SESSION_ID, "hp_change": -10, "reason": "combat"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["current_hp"] == 90

        mock_update_hp.assert_called_once_with(
            player_id=MOCK_PLAYER_ID,
            session_id=MOCK_SESSION_ID,
            hp_change=-10,
            reason="combat",
        )


@pytest.mark.asyncio
async def test_update_inventory(async_client: AsyncClient):
    mock_response = {
        "player_id": MOCK_PLAYER_ID,
        "inventory": [{"item_id": 5, "item_name": "Sword", "quantity": 3}],
    }

    with patch(
        "state_db.router.inventory_update", new=AsyncMock(return_value=mock_response)
    ) as mock_inv_update:
        response = await async_client.put(
            "/state/inventory/update",
            json={"player_id": MOCK_PLAYER_ID, "item_id": 5, "quantity": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["inventory"]) == 1

        mock_inv_update.assert_called_once_with(
            player_id=MOCK_PLAYER_ID, item_id=5, quantity=3
        )
