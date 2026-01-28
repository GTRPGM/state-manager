from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

# Mock data
MOCK_SESSION_ID = "test-session-id"
MOCK_PLAYER_ID = "test-player-id"
MOCK_NPC_ID = "test-npc-id"
MOCK_ITEM_ID = 5


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
            json={"session_id": MOCK_SESSION_ID, "hp_change": -10},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["current_hp"] == 90


@pytest.mark.asyncio
async def test_update_player_stats(async_client: AsyncClient):
    mock_response = {
        "player_id": MOCK_PLAYER_ID,
        "stats": {"strength": 12, "intelligence": 11},
    }

    with patch(
        "state_db.repositories.PlayerRepository.update_stats",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.put(
            f"/state/player/{MOCK_PLAYER_ID}/stats",
            json={
                "session_id": MOCK_SESSION_ID,
                "stat_changes": {"strength": 2, "intelligence": 1},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["stats"]["strength"] == 12


@pytest.mark.asyncio
async def test_update_inventory(async_client: AsyncClient):
    mock_response = {"player_id": MOCK_PLAYER_ID, "item_id": MOCK_ITEM_ID, "quantity": 5}

    with patch(
        "state_db.repositories.PlayerRepository.update_inventory",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.put(
            "/state/inventory/update",
            json={"player_id": MOCK_PLAYER_ID, "item_id": MOCK_ITEM_ID, "quantity": 5},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["quantity"] == 5


@pytest.mark.asyncio
async def test_update_npc_affinity(async_client: AsyncClient):
    mock_response = {
        "player_id": MOCK_PLAYER_ID,
        "npc_id": MOCK_NPC_ID,
        "new_affinity": 60,
    }

    with patch(
        "state_db.repositories.PlayerRepository.update_npc_affinity",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.put(
            "/state/npc/affinity",
            json={
                "player_id": MOCK_PLAYER_ID,
                "npc_id": MOCK_NPC_ID,
                "affinity_change": 10,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["new_affinity"] == 60


@pytest.mark.asyncio
async def test_update_location(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.update_location",
        new=AsyncMock(),
    ) as mock_update:
        response = await async_client.put(
            f"/state/session/{MOCK_SESSION_ID}/location",
            json={"new_location": "Dark Forest"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["location"] == "Dark Forest"
        mock_update.assert_called_once_with(MOCK_SESSION_ID, "Dark Forest")
