from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from state_db.repositories.trace import TraceRepository


@pytest.mark.asyncio
async def test_trace_repository_list_and_optional_paths():
    repo = TraceRepository()

    with patch(
        "state_db.repositories.trace.run_sql_query", new_callable=AsyncMock
    ) as mock_query:
        mock_query.side_effect = [
            [{"turn": 1}],
            [{"turn": 2}],
            [{"turn": 1}, {"turn": 2}],
            [{"type": "player", "count": 2}],
            [{"turn": 1, "duration": 1.2}],
            [{"turn": 9}],
            [],
            [],
            [],
            [],
            [],
            [],
        ]

        assert await repo.get_turn_history("s1") == [{"turn": 1}]
        assert await repo.get_recent_turns("s1", limit=5) == [{"turn": 2}]
        assert await repo.get_turn_range("s1", 1, 2) == [{"turn": 1}, {"turn": 2}]
        assert await repo.get_turn_statistics_by_type("s1") == [
            {"type": "player", "count": 2}
        ]
        assert await repo.get_turn_duration_analysis("s1") == [
            {"turn": 1, "duration": 1.2}
        ]
        assert await repo.get_latest_turn("s1") == {"turn": 9}

        assert await repo.get_turn_history("s1") == []
        assert await repo.get_recent_turns("s1") == []
        assert await repo.get_turn_range("s1", 3, 4) == []
        assert await repo.get_turn_statistics_by_type("s1") == []
        assert await repo.get_turn_duration_analysis("s1") == []
        assert await repo.get_latest_turn("s1") is None


@pytest.mark.asyncio
async def test_trace_repository_detail_and_summary_paths():
    repo = TraceRepository()

    with patch(
        "state_db.repositories.trace.run_sql_query", new_callable=AsyncMock
    ) as mock_query:
        mock_query.side_effect = [
            [{"turn": 3, "note": "ok"}],
            [{"total_turns": 3}],
            [],
            [],
        ]

        assert await repo.get_turn_details("s1", 3) == {"turn": 3, "note": "ok"}
        assert await repo.get_turn_summary("s1") == {"total_turns": 3}

        with pytest.raises(HTTPException) as exc:
            await repo.get_turn_details("s1", 404)
        assert exc.value.status_code == 404
        assert exc.value.detail == "Turn not found"

        assert await repo.get_turn_summary("s1") == {}
