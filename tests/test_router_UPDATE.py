from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

# Mock data - 유효한 UUID 형식 사용
MOCK_SESSION_ID = "550e8400-e29b-41d4-a716-446655440001"
MOCK_PLAYER_ID = "550e8400-e29b-41d4-a716-446655440002"
MOCK_NPC_ID = "550e8400-e29b-41d4-a716-446655440004"
MOCK_ENEMY_ID = "550e8400-e29b-41d4-a716-446655440003"
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
            json={"session_id": MOCK_SESSION_ID, "hp_change": -10, "reason": "combat"},
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
    mock_response = {
        "player_id": MOCK_PLAYER_ID,
        "item_id": MOCK_ITEM_ID,
        "quantity": 5,
    }

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
    mock_response = {
        "session_id": MOCK_SESSION_ID,
        "location": "Dark Forest",
    }
    # [수정됨] SessionRepository -> ProgressRepository
    with patch(
        "state_db.repositories.ProgressRepository.update_location",
        new=AsyncMock(return_value=mock_response),
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


@pytest.mark.asyncio
async def test_update_enemy_hp(async_client: AsyncClient):
    mock_response = {
        "enemy_instance_id": MOCK_ENEMY_ID,
        "name": "Goblin",
        "current_hp": 40,
        "max_hp": 50,
        "hp_change": -10,
        "is_defeated": False,
    }

    with patch(
        "state_db.repositories.EntityRepository.update_enemy_hp",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.put(
            f"/state/enemy/{MOCK_ENEMY_ID}/hp",
            json={"session_id": MOCK_SESSION_ID, "hp_change": -10},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["current_hp"] == 40


@pytest.mark.asyncio
async def test_defeat_enemy(async_client: AsyncClient):
    mock_response = {
        "enemy_instance_id": MOCK_ENEMY_ID,
        "status": "defeated",
    }
    with patch(
        "state_db.repositories.EntityRepository.defeat_enemy",
        new=AsyncMock(return_value=mock_response),
    ) as mock_defeat:
        response = await async_client.post(
            f"/state/enemy/{MOCK_ENEMY_ID}/defeat?session_id={MOCK_SESSION_ID}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["enemy_instance_id"] == MOCK_ENEMY_ID
        assert data["data"]["status"] == "defeated"
        mock_defeat.assert_called_once_with(MOCK_SESSION_ID, MOCK_ENEMY_ID)


@pytest.mark.asyncio
async def test_earn_item(async_client: AsyncClient):
    mock_response = {
        "player_id": MOCK_PLAYER_ID,
        "item_id": MOCK_ITEM_ID,
        "quantity": 3,
        "total_quantity": 8,
    }

    with patch(
        "state_db.repositories.PlayerRepository.earn_item",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.post(
            "/state/player/item/earn",
            json={
                "session_id": MOCK_SESSION_ID,
                "player_id": MOCK_PLAYER_ID,
                "item_id": MOCK_ITEM_ID,
                "quantity": 3,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["quantity"] == 3


@pytest.mark.asyncio
async def test_use_item(async_client: AsyncClient):
    mock_response = {
        "player_id": MOCK_PLAYER_ID,
        "item_id": MOCK_ITEM_ID,
        "quantity": 1,
        "remaining_quantity": 7,
    }

    with patch(
        "state_db.repositories.PlayerRepository.use_item",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.post(
            "/state/player/item/use",
            json={
                "session_id": MOCK_SESSION_ID,
                "player_id": MOCK_PLAYER_ID,
                "item_id": MOCK_ITEM_ID,
                "quantity": 1,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["quantity"] == 1
