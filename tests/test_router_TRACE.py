from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

MOCK_SESSION_ID = "550e8400-e29b-41d4-a716-446655440001"
MOCK_TURN_NUMBER = 5


@pytest.mark.asyncio
async def test_get_turn_history(async_client: AsyncClient):
    mock_turns = [{"history_id": 1, "session_id": MOCK_SESSION_ID, "turn_number": 1}]
    with patch(
        "state_db.repositories.TraceRepository.get_turn_history",
        new=AsyncMock(return_value=mock_turns),
    ):
        response = await async_client.get(f"/state/session/{MOCK_SESSION_ID}/turns")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_recent_turns(async_client: AsyncClient):
    mock_turns = [{"turn_number": 5}]
    with patch(
        "state_db.repositories.TraceRepository.get_recent_turns",
        new=AsyncMock(return_value=mock_turns),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turns/recent"
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_turn_details(async_client: AsyncClient):
    mock_turn = {"turn_number": MOCK_TURN_NUMBER}
    with patch(
        "state_db.repositories.TraceRepository.get_turn_details",
        new=AsyncMock(return_value=mock_turn),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turn/{MOCK_TURN_NUMBER}"
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_turn_range(async_client: AsyncClient):
    mock_turns = [{"turn_number": 1}]
    with patch(
        "state_db.repositories.TraceRepository.get_turn_range",
        new=AsyncMock(return_value=mock_turns),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turns/range?start=1&end=3"
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_latest_turn(async_client: AsyncClient):
    mock_turn = {"turn_number": 10}
    with patch(
        "state_db.repositories.TraceRepository.get_latest_turn",
        new=AsyncMock(return_value=mock_turn),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turn/latest"
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_turn_statistics_by_type(async_client: AsyncClient):
    mock_stats = [{"turn_type": "movement", "count": 10}]
    with patch(
        "state_db.repositories.TraceRepository.get_turn_statistics_by_type",
        new=AsyncMock(return_value=mock_stats),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turns/statistics/by-type"
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_turn_duration_analysis(async_client: AsyncClient):
    mock_analysis = [{"turn_number": 1}]
    with patch(
        "state_db.repositories.TraceRepository.get_turn_duration_analysis",
        new=AsyncMock(return_value=mock_analysis),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turns/duration-analysis"
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_turn_summary(async_client: AsyncClient):
    mock_summary = {"total_turns": 20}
    with patch(
        "state_db.repositories.TraceRepository.get_turn_summary",
        new=AsyncMock(return_value=mock_summary),
    ):
        response = await async_client.get(
            f"/state/session/{MOCK_SESSION_ID}/turns/summary"
        )
        assert response.status_code == 200
