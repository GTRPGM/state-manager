from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

MOCK_SESSION_ID = "550e8400-e29b-41d4-a716-446655440001"
MOCK_NPC_ID = "550e8400-e29b-41d4-a716-446655440004"
MOCK_ENEMY_ID = "550e8400-e29b-41d4-a716-446655440005"


@pytest.mark.asyncio
async def test_get_all_sessions(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.get_all_sessions",
        new=AsyncMock(return_value=[]),
    ):
        response = await async_client.get("/state/sessions")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_active_sessions(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.get_active_sessions",
        new=AsyncMock(return_value=[]),
    ):
        response = await async_client.get("/state/sessions/active")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_session_info(async_client: AsyncClient):
    mock_info = {
        "session_id": MOCK_SESSION_ID,
        "scenario_id": "test",
        "current_act": 1,
        "current_sequence": 1,
        "status": "active",
    }
    with patch(
        "state_db.repositories.SessionRepository.get_info",
        new=AsyncMock(return_value=mock_info),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_player_state(async_client: AsyncClient):
    mock_state = {"player": {"hp": 100, "gold": 50}, "player_npc_relations": []}
    with patch(
        "state_db.repositories.PlayerRepository.get_full_state",
        new=AsyncMock(return_value=mock_state),
    ):
        response = await async_client.get("/state/player/test-id")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_npcs(async_client: AsyncClient):
    mock_npcs = [
        {
            "npc_id": MOCK_NPC_ID,
            "scenario_npc_id": "n1",
            "name": "Test",
            "description": "D",
            "tags": [],
        }
    ]
    with patch(
        "state_db.repositories.EntityRepository.get_session_npcs",
        new=AsyncMock(return_value=mock_npcs),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/npcs")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_enemies(async_client: AsyncClient):
    mock_enemies = [
        {
            "enemy_instance_id": MOCK_ENEMY_ID,
            "scenario_enemy_id": "e1",
            "name": "Test",
            "description": "D",
            "tags": [],
        }
    ]
    with patch(
        "state_db.repositories.EntityRepository.get_session_enemies",
        new=AsyncMock(return_value=mock_enemies),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/enemies")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_phase(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.get_phase",
        new=AsyncMock(
            return_value={"session_id": "id", "current_phase": "exploration"}
        ),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/phase")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_turn(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.get_turn",
        new=AsyncMock(return_value={"session_id": "id", "current_turn": 1}),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/turn")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_act(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.get_act",
        new=AsyncMock(return_value={"current_act": 1}),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/act")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_sequence(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.get_sequence",
        new=AsyncMock(return_value={"current_sequence": 1}),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/sequence")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_location(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.get_location",
        new=AsyncMock(return_value={"location": "Test"}),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/location")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_progress(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.get_progress",
        new=AsyncMock(return_value={"progress": 50}),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/progress")
        assert response.status_code == 200
