from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

# Mock data
MOCK_SESSION_ID = "test-session-id"
MOCK_ENEMY_ID = "test-enemy-id"
MOCK_NPC_ID = "test-npc-id"


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
async def test_pause_session(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.pause", new=AsyncMock()
    ) as mock_pause:
        response = await async_client.post(f"/state/session/{MOCK_SESSION_ID}/pause")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        mock_pause.assert_called_once_with(MOCK_SESSION_ID)


@pytest.mark.asyncio
async def test_resume_session(async_client: AsyncClient):
    with patch(
        "state_db.repositories.SessionRepository.resume", new=AsyncMock()
    ) as mock_resume:
        response = await async_client.post(f"/state/session/{MOCK_SESSION_ID}/resume")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        mock_resume.assert_called_once_with(MOCK_SESSION_ID)


@pytest.mark.asyncio
async def test_spawn_enemy(async_client: AsyncClient):
    mock_response = {
        "id": MOCK_ENEMY_ID,
        "name": "Goblin",
    }

    with patch(
        "state_db.repositories.EntityRepository.spawn_enemy",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.post(
            f"/state/session/{MOCK_SESSION_ID}/enemy/spawn",
            json={
                "enemy_id": 1,
                "name": "Goblin",
                "max_hp": 50,
                "current_hp": 50,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["id"] == MOCK_ENEMY_ID


@pytest.mark.asyncio
async def test_remove_enemy(async_client: AsyncClient):
    mock_response = {
        "status": "success",
    }

    with patch(
        "state_db.repositories.EntityRepository.remove_enemy",
        new=AsyncMock(return_value=mock_response),
    ) as mock_remove:
        response = await async_client.delete(
            f"/state/session/{MOCK_SESSION_ID}/enemy/{MOCK_ENEMY_ID}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        mock_remove.assert_called_once_with(MOCK_SESSION_ID, MOCK_ENEMY_ID)


@pytest.mark.asyncio
async def test_spawn_npc(async_client: AsyncClient):
    mock_response = {
        "id": MOCK_NPC_ID,
        "name": "Village Elder",
    }

    with patch(
        "state_db.repositories.EntityRepository.spawn_npc",
        new=AsyncMock(return_value=mock_response),
    ):
        response = await async_client.post(
            f"/state/session/{MOCK_SESSION_ID}/npc/spawn",
            json={
                "npc_id": 1,
                "name": "Village Elder",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["id"] == MOCK_NPC_ID


@pytest.mark.asyncio
async def test_remove_npc(async_client: AsyncClient):
    mock_response = {
        "status": "success",
    }

    with patch(
        "state_db.repositories.EntityRepository.remove_npc",
        new=AsyncMock(return_value=mock_response),
    ) as mock_remove:
        response = await async_client.delete(
            f"/state/session/{MOCK_SESSION_ID}/npc/{MOCK_NPC_ID}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        mock_remove.assert_called_once_with(MOCK_SESSION_ID, MOCK_NPC_ID)


@pytest.mark.asyncio
async def test_change_phase(async_client: AsyncClient):
    mock_response = {
        "session_id": MOCK_SESSION_ID,
        "current_phase": "combat",
    }

    with patch(
        "state_db.repositories.SessionRepository.change_phase",
        new=AsyncMock(return_value=mock_response),
    ) as mock_change:
        response = await async_client.put(
            f"/state/session/{MOCK_SESSION_ID}/phase",
            json={"new_phase": "combat"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["current_phase"] == "combat"
        mock_change.assert_called_once_with(MOCK_SESSION_ID, "combat")


@pytest.mark.asyncio
async def test_add_turn(async_client: AsyncClient):
    mock_response = {
        "session_id": MOCK_SESSION_ID,
        "current_turn": 6,
    }

    with patch(
        "state_db.repositories.SessionRepository.add_turn",
        new=AsyncMock(return_value=mock_response),
    ) as mock_add:
        response = await async_client.post(
            f"/state/session/{MOCK_SESSION_ID}/turn/add"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["current_turn"] == 6
        mock_add.assert_called_once_with(MOCK_SESSION_ID)


@pytest.mark.asyncio
async def test_change_act(async_client: AsyncClient):
    mock_response = {
        "session_id": MOCK_SESSION_ID,
        "current_act": 2,
        "current_phase": "exploration",
    }

    with patch(
        "state_db.repositories.SessionRepository.change_act",
        new=AsyncMock(return_value=mock_response),
    ) as mock_change:
        response = await async_client.put(
            f"/state/session/{MOCK_SESSION_ID}/act",
            json={"new_act": 2},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["current_act"] == 2
        mock_change.assert_called_once_with(MOCK_SESSION_ID, 2)


@pytest.mark.asyncio
async def test_change_sequence(async_client: AsyncClient):
    mock_response = {
        "session_id": MOCK_SESSION_ID,
        "current_sequence": 4,
    }

    with patch(
        "state_db.repositories.SessionRepository.change_sequence",
        new=AsyncMock(return_value=mock_response),
    ) as mock_change:
        response = await async_client.put(
            f"/state/session/{MOCK_SESSION_ID}/sequence",
            json={"new_sequence": 4},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["current_sequence"] == 4
        mock_change.assert_called_once_with(MOCK_SESSION_ID, 4)
