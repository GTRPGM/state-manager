from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

MOCK_SESSION_ID = "00000000-0000-0000-0000-000000000000"
MOCK_ENEMY_ID = "enemy-123"
MOCK_NPC_ID = "npc-123"


@pytest.mark.asyncio
async def test_end_session(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.end",
        new=AsyncMock(return_value=None),
    ):
        response = await async_client.post(f"/state/session/{MOCK_SESSION_ID}/end")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_pause_session(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.pause",
        new=AsyncMock(return_value=None),
    ):
        response = await async_client.post(f"/state/session/{MOCK_SESSION_ID}/pause")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_resume_session(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.resume",
        new=AsyncMock(return_value=None),
    ):
        response = await async_client.post(f"/state/session/{MOCK_SESSION_ID}/resume")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_spawn_enemy(async_client: AsyncClient):
    mock_response = {"id": MOCK_ENEMY_ID, "name": "Goblin"}
    with patch(
        "state_db.repositories.EntityRepository.spawn_enemy",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.post(
            f"/state/session/{MOCK_SESSION_ID}/enemy/spawn",
            json={"scenario_enemy_id": "enemy-goblin", "rule_id": 1, "name": "Goblin"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_remove_enemy(async_client: AsyncClient):
    with patch(
        "state_db.repositories.EntityRepository.remove_enemy",
        new=AsyncMock(return_value={}),
    ):
        response = await async_client.delete(
            f"/state/session/{MOCK_SESSION_ID}/enemy/{MOCK_ENEMY_ID}"
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_spawn_npc(async_client: AsyncClient):
    mock_response = {"id": MOCK_NPC_ID, "name": "Elder"}
    with patch(
        "state_db.repositories.EntityRepository.spawn_npc",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.post(
            f"/state/session/{MOCK_SESSION_ID}/npc/spawn",
            json={"scenario_npc_id": "npc-elder", "rule_id": 101, "name": "Elder"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_remove_npc(async_client: AsyncClient):
    with patch(
        "state_db.repositories.EntityRepository.remove_npc",
        new=AsyncMock(return_value={}),
    ):
        response = await async_client.delete(
            f"/state/session/{MOCK_SESSION_ID}/npc/{MOCK_NPC_ID}"
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_turn(async_client: AsyncClient):
    mock_response = {"session_id": MOCK_SESSION_ID, "current_turn": 2}
    with patch(
        "state_db.repositories.LifecycleStateRepository.add_turn",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.post(f"/state/session/{MOCK_SESSION_ID}/turn/add")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_change_act(async_client: AsyncClient):
    mock_response = {
        "session_id": MOCK_SESSION_ID,
        "current_act": 2,
        "current_act_id": "act-2",
    }
    with patch(
        "state_db.repositories.scenario.ScenarioRepository.advance_act",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.put(
            f"/state/session/{MOCK_SESSION_ID}/act",
            json={"new_act": 2, "new_act_id": "act-2", "new_sequence_id": "seq-2-1"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_change_sequence(async_client: AsyncClient):
    mock_response = {
        "session_id": MOCK_SESSION_ID,
        "current_sequence": 2,
        "current_sequence_id": "seq-2",
    }
    with patch(
        "state_db.repositories.scenario.ScenarioRepository.update_sequence",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.put(
            f"/state/session/{MOCK_SESSION_ID}/sequence",
            json={"new_sequence": 2, "new_sequence_id": "seq-2"},
        )
        assert response.status_code == 200
