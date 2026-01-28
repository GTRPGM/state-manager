from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

# Mock data
MOCK_SESSION_ID = "test-session-id"
MOCK_PLAYER_ID = "test-player-id"
MOCK_SCENARIO_ID = "550e8400-e29b-41d4-a716-446655440000"
MOCK_ENEMY_ID = "test-enemy-id"
MOCK_NPC_ID = "test-npc-id"


@pytest.mark.asyncio
async def test_get_active_sessions(async_client: AsyncClient):
    mock_sessions = [
        {
            "session_id": MOCK_SESSION_ID,
            "scenario_id": MOCK_SCENARIO_ID,
            "player_id": MOCK_PLAYER_ID,
            "current_act": 1,
            "current_sequence": 1,
            "status": "active",
        }
    ]

    with patch(
        "state_db.repositories.SessionRepository.get_active_sessions",
        new=AsyncMock(return_value=mock_sessions),
    ):
        response = await async_client.get("/state/sessions/active")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 1


@pytest.mark.asyncio
async def test_get_session(async_client: AsyncClient):
    mock_session = {
        "session_id": MOCK_SESSION_ID,
        "scenario_id": MOCK_SCENARIO_ID,
        "player_id": MOCK_PLAYER_ID,
        "current_act": 1,
        "current_sequence": 1,
        "location": "Starting Town",
        "status": "active",
    }

    with patch(
        "state_db.repositories.SessionRepository.get_info",
        new=AsyncMock(return_value=mock_session),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["session_id"] == MOCK_SESSION_ID


@pytest.mark.asyncio
async def test_get_player(async_client: AsyncClient):
    mock_player = {
        "player": {
            "hp": 100,
            "gold": 50,
            "items": [],
        },
        "player_npc_relations": [],
    }

    with patch(
        "state_db.repositories.PlayerRepository.get_full_state",
        new=AsyncMock(return_value=mock_player),
    ):
        response = await async_client.get(f"/state/player/{MOCK_PLAYER_ID}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["player"]["hp"] == 100


@pytest.mark.asyncio
async def test_get_inventory(async_client: AsyncClient):
    mock_items = [
        {"item_id": 1, "item_name": "Health Potion", "quantity": 5},
        {"item_id": 2, "item_name": "Mana Potion", "quantity": 3},
    ]

    with patch(
        "state_db.repositories.PlayerRepository.get_inventory",
        new=AsyncMock(return_value=mock_items),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/inventory")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_npcs(async_client: AsyncClient):
    mock_npcs = [
        {
            "npc_id": MOCK_NPC_ID,
            "name": "Test NPC",
            "description": "A test NPC",
            "hp": 100,
            "tags": [],
        }
    ]

    with patch(
        "state_db.repositories.EntityRepository.get_session_npcs",
        new=AsyncMock(return_value=mock_npcs),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/npcs")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 1


@pytest.mark.asyncio
async def test_get_enemies(async_client: AsyncClient):
    mock_enemies = [
        {
            "enemy_instance_id": MOCK_ENEMY_ID,
            "enemy_id": 1,
            "name": "Test Enemy",
            "hp": 50,
            "current_hp": 50,
            "is_active": True,
        }
    ]

    with patch(
        "state_db.repositories.EntityRepository.get_session_enemies",
        new=AsyncMock(return_value=mock_enemies),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/enemies")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 1


@pytest.mark.asyncio
async def test_get_phase(async_client: AsyncClient):
    mock_phase = {"session_id": MOCK_SESSION_ID, "current_phase": "exploration"}

    with patch(
        "state_db.repositories.SessionRepository.get_phase",
        new=AsyncMock(return_value=mock_phase),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/phase")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["current_phase"] == "exploration"


@pytest.mark.asyncio
async def test_get_turn(async_client: AsyncClient):
    mock_turn = {"session_id": MOCK_SESSION_ID, "current_turn": 5}

    with patch(
        "state_db.repositories.SessionRepository.get_turn",
        new=AsyncMock(return_value=mock_turn),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/turn")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["current_turn"] == 5
