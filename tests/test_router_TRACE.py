from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

# Mock data - 유효한 UUID 형식 사용
MOCK_SESSION_ID = "550e8400-e29b-41d4-a716-446655440001"
MOCK_TURN_NUMBER = 5


# ====================================================================
# Turn History Tests
# ====================================================================


@pytest.mark.asyncio
async def test_get_turn_history(async_client: AsyncClient):
    mock_turns = [
        {
            "history_id": 1,
            "session_id": MOCK_SESSION_ID,
            "turn_number": 1,
            "phase_at_turn": "exploration",
            "turn_type": "movement",
            "state_changes": {},
            "related_entities": [],
            "created_at": "2025-01-01T00:00:00",
        },
        {
            "history_id": 2,
            "session_id": MOCK_SESSION_ID,
            "turn_number": 2,
            "phase_at_turn": "combat",
            "turn_type": "attack",
            "state_changes": {},
            "related_entities": [],
            "created_at": "2025-01-01T00:01:00",
        },
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_turn_history",
        new=AsyncMock(return_value=mock_turns),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/turns")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_recent_turns(async_client: AsyncClient):
    mock_turns = [
        {
            "turn_number": 5,
            "phase_at_turn": "combat",
            "created_at": "2025-01-01T00:05:00",
        }
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_recent_turns",
        new=AsyncMock(return_value=mock_turns),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turns/recent?limit=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 1


@pytest.mark.asyncio
async def test_get_turn_details(async_client: AsyncClient):
    mock_turn = {
        "turn_number": MOCK_TURN_NUMBER,
        "phase_at_turn": "combat",
        "turn_type": "attack",
        "state_changes": {"hp_change": -10},
        "related_entities": ["enemy-1"],
    }

    with patch(
        "state_db.repositories.TraceRepository.get_turn_details",
        new=AsyncMock(return_value=mock_turn),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turn/{MOCK_TURN_NUMBER}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["turn_number"] == MOCK_TURN_NUMBER


@pytest.mark.asyncio
async def test_get_turn_range(async_client: AsyncClient):
    mock_turns = [
        {"turn_number": 1, "phase_at_turn": "exploration"},
        {"turn_number": 2, "phase_at_turn": "combat"},
        {"turn_number": 3, "phase_at_turn": "combat"},
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_turn_range",
        new=AsyncMock(return_value=mock_turns),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turns/range?start=1&end=3"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 3


@pytest.mark.asyncio
async def test_get_latest_turn(async_client: AsyncClient):
    mock_turn = {
        "history_id": 10,
        "session_id": MOCK_SESSION_ID,
        "turn_number": 10,
        "phase_at_turn": "rest",
        "turn_type": "rest",
        "state_changes": {},
        "related_entities": [],
        "created_at": "2025-01-01T00:10:00",
    }

    with patch(
        "state_db.repositories.TraceRepository.get_latest_turn",
        new=AsyncMock(return_value=mock_turn),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turn/latest"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["turn_number"] == 10


@pytest.mark.asyncio
async def test_get_turn_statistics_by_phase(async_client: AsyncClient):
    mock_stats = [
        {"phase": "exploration", "turn_count": 5, "avg_duration": 30.5},
        {"phase": "combat", "turn_count": 8, "avg_duration": 45.2},
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_turn_statistics_by_phase",
        new=AsyncMock(return_value=mock_stats),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turns/statistics/by-phase"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_turn_statistics_by_type(async_client: AsyncClient):
    mock_stats = [
        {"turn_type": "movement", "count": 10},
        {"turn_type": "attack", "count": 15},
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_turn_statistics_by_type",
        new=AsyncMock(return_value=mock_stats),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turns/statistics/by-type"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_turn_duration_analysis(async_client: AsyncClient):
    mock_analysis = [
        {"turn_number": 1, "duration_seconds": 30, "next_turn_gap": 5},
        {"turn_number": 2, "duration_seconds": 45, "next_turn_gap": 10},
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_turn_duration_analysis",
        new=AsyncMock(return_value=mock_analysis),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turns/duration-analysis"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_turn_summary(async_client: AsyncClient):
    mock_summary = {
        "total_turns": 20,
        "average_turn_duration": 35.5,
        "most_common_phase": "combat",
        "total_duration_seconds": 710,
    }

    with patch(
        "state_db.repositories.TraceRepository.get_turn_summary",
        new=AsyncMock(return_value=mock_summary),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turns/summary"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["total_turns"] == 20


# ====================================================================
# Phase History Tests
# ====================================================================


@pytest.mark.asyncio
async def test_get_phase_history(async_client: AsyncClient):
    mock_phases = [
        {
            "phase_id": 1,
            "session_id": MOCK_SESSION_ID,
            "from_phase": None,
            "to_phase": "exploration",
            "changed_at_turn": 0,
            "created_at": "2025-01-01T00:00:00",
        },
        {
            "phase_id": 2,
            "session_id": MOCK_SESSION_ID,
            "from_phase": "exploration",
            "to_phase": "combat",
            "changed_at_turn": 5,
            "created_at": "2025-01-01T00:05:00",
        },
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_phase_history",
        new=AsyncMock(return_value=mock_phases),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/phases")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_recent_phases(async_client: AsyncClient):
    mock_phases = [
        {
            "from_phase": "combat",
            "to_phase": "rest",
            "changed_at_turn": 10,
            "created_at": "2025-01-01T00:10:00",
        }
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_recent_phases",
        new=AsyncMock(return_value=mock_phases),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/phases/recent?limit=5"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 1


@pytest.mark.asyncio
async def test_get_phase_by_phase(async_client: AsyncClient):
    mock_phases = [
        {"from_phase": "exploration", "to_phase": "combat", "changed_at_turn": 3},
        {"from_phase": "rest", "to_phase": "combat", "changed_at_turn": 8},
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_phase_by_phase",
        new=AsyncMock(return_value=mock_phases),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/phases/by-phase?phase=combat"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_phase_range(async_client: AsyncClient):
    mock_phases = [
        {"from_phase": "exploration", "to_phase": "combat", "changed_at_turn": 5},
        {"from_phase": "combat", "to_phase": "rest", "changed_at_turn": 8},
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_phase_range",
        new=AsyncMock(return_value=mock_phases),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/phases/range?start_turn=0&end_turn=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_latest_phase(async_client: AsyncClient):
    mock_phase = {
        "from_phase": "combat",
        "to_phase": "rest",
        "changed_at_turn": 15,
        "created_at": "2025-01-01T00:15:00",
    }

    with patch(
        "state_db.repositories.TraceRepository.get_latest_phase",
        new=AsyncMock(return_value=mock_phase),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/phase/latest"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["to_phase"] == "rest"


@pytest.mark.asyncio
async def test_get_phase_statistics(async_client: AsyncClient):
    mock_stats = [
        {
            "phase": "exploration",
            "total_time_seconds": 300,
            "transition_count": 3,
            "avg_time_seconds": 100,
        },
        {
            "phase": "combat",
            "total_time_seconds": 450,
            "transition_count": 5,
            "avg_time_seconds": 90,
        },
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_phase_statistics",
        new=AsyncMock(return_value=mock_stats),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/phases/statistics"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_phase_pattern(async_client: AsyncClient):
    mock_pattern = [
        {"from_phase": "exploration", "to_phase": "combat", "count": 5},
        {"from_phase": "combat", "to_phase": "rest", "count": 4},
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_phase_pattern",
        new=AsyncMock(return_value=mock_pattern),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/phases/pattern"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_phase_summary(async_client: AsyncClient):
    mock_summary = [
        {
            "phase": "exploration",
            "count": 8,
            "total_duration_seconds": 480,
            "percentage": 40.0,
        },
        {
            "phase": "combat",
            "count": 12,
            "total_duration_seconds": 720,
            "percentage": 60.0,
        },
    ]

    with patch(
        "state_db.repositories.TraceRepository.get_phase_summary",
        new=AsyncMock(return_value=mock_summary),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/phases/summary"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2
