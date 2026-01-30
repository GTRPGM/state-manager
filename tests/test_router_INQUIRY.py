from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

MOCK_SESSION_ID = "00000000-0000-0000-0000-000000000000"
MOCK_PLAYER_ID = "player-123"
MOCK_ITEM_ID = 1
MOCK_SCENARIO_ID = "scenario-123"


@pytest.mark.asyncio
async def test_get_all_scenarios(async_client: AsyncClient):
    with patch(
        "state_db.repositories.ScenarioRepository.get_all_scenarios",
        new=AsyncMock(return_value=[]),
    ):
        response = await async_client.get("/state/scenarios")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_scenario_detail(async_client: AsyncClient):
    with patch(
        "state_db.repositories.ScenarioRepository.get_scenario",
        new=AsyncMock(
            return_value={
                "scenario_id": MOCK_SCENARIO_ID,
                "title": "Test",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        ),
    ):
        response = await async_client.get(f"/state/scenario/{MOCK_SCENARIO_ID}")
        assert response.status_code == 200


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
    with patch(
        "state_db.repositories.SessionRepository.get_info",
        new=AsyncMock(
            return_value={
                "session_id": MOCK_SESSION_ID,
                "scenario_id": "id",
                "current_act": 1,
                "current_sequence": 1,
                "current_phase": "exploration",
                "current_turn": 1,
                "location": "Arena",
                "status": "active",
            }
        ),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_player_state(async_client: AsyncClient):
    with patch(
        "state_db.repositories.PlayerRepository.get_full_state",
        new=AsyncMock(
            return_value={"player": {"hp": 100, "gold": 0}, "player_npc_relations": []}
        ),
    ):
        response = await async_client.get(f"/state/player/{MOCK_PLAYER_ID}")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_inventory(async_client: AsyncClient):
    with patch(
        "state_db.repositories.PlayerRepository.get_inventory",
        new=AsyncMock(return_value=[]),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/inventory")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_npcs(async_client: AsyncClient):
    with patch(
        "state_db.repositories.EntityRepository.get_session_npcs",
        new=AsyncMock(return_value=[]),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/npcs")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_enemies(async_client: AsyncClient):
    with patch(
        "state_db.repositories.EntityRepository.get_session_enemies",
        new=AsyncMock(return_value=[]),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/enemies")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_phase(async_client: AsyncClient):
    with patch(
        "state_db.repositories.LifecycleStateRepository.get_phase",
        new=AsyncMock(
            return_value={"session_id": "id", "current_phase": "exploration"}
        ),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/phase")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_turn(async_client: AsyncClient):
    with patch(
        "state_db.repositories.LifecycleStateRepository.get_turn",
        new=AsyncMock(return_value={"session_id": "id", "current_turn": 1}),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/turn")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_act(async_client: AsyncClient):
    with patch(
        "state_db.repositories.ProgressRepository.get_act",
        new=AsyncMock(return_value={"current_act": 1}),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/act")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_sequence(async_client: AsyncClient):
    with patch(
        "state_db.repositories.ProgressRepository.get_sequence",
        new=AsyncMock(return_value={"current_sequence": 1}),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/sequence")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_location(async_client: AsyncClient):
    with patch(
        "state_db.repositories.ProgressRepository.get_location",
        new=AsyncMock(return_value={"location": "Test"}),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/location")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_progress(async_client: AsyncClient):
    with patch(
        "state_db.repositories.ProgressRepository.get_progress",
        new=AsyncMock(return_value={"progress": 50}),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/progress")
        assert response.status_code == 200
