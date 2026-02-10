from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from state_db.repositories.progress import ProgressRepository


@pytest.mark.asyncio
async def test_progress_repository_mutation_commands():
    repo = ProgressRepository()

    with patch(
        "state_db.repositories.progress.run_sql_command", new_callable=AsyncMock
    ) as mock_cmd:
        await repo.update_location("s1", "town")
        await repo.change_act("s1", 2)
        await repo.change_sequence("s1", 3)

    assert mock_cmd.await_count == 3


@pytest.mark.asyncio
async def test_progress_repository_getters_success():
    repo = ProgressRepository()
    fake_row = {"session_id": "s1", "value": 1}

    with patch(
        "state_db.repositories.progress.run_sql_query", new_callable=AsyncMock
    ) as mock_query:
        mock_query.return_value = [fake_row]

        assert await repo.get_location("s1") == fake_row
        assert await repo.get_progress("s1") == fake_row
        assert await repo.get_act("s1") == fake_row
        assert await repo.get_sequence("s1") == fake_row
        assert await repo.act_check("s1") == fake_row
        assert await repo.limit_sequence("s1") == fake_row


@pytest.mark.asyncio
async def test_progress_repository_model_results_success():
    repo = ProgressRepository()

    with patch(
        "state_db.repositories.progress.run_sql_query", new_callable=AsyncMock
    ) as mock_query:
        mock_query.side_effect = [
            [{"session_id": "s1", "current_act": 2}],
            [{"session_id": "s1", "current_act": 1}],
            [{"session_id": "s1", "current_sequence": 3}],
            [{"session_id": "s1", "current_sequence": 2}],
        ]

        add_act = await repo.add_act("s1")
        back_act = await repo.back_act("s1")
        add_seq = await repo.add_sequence("s1")
        back_seq = await repo.back_sequence("s1")

    assert add_act.current_act == 2
    assert back_act.current_act == 1
    assert add_seq.current_sequence == 3
    assert back_seq.current_sequence == 2


@pytest.mark.asyncio
async def test_progress_repository_not_found_paths_raise():
    repo = ProgressRepository()

    with patch(
        "state_db.repositories.progress.run_sql_query", new_callable=AsyncMock
    ) as mock_query:
        mock_query.return_value = []

        methods = [
            repo.get_location,
            repo.get_progress,
            repo.get_act,
            repo.add_act,
            repo.back_act,
            repo.act_check,
            repo.get_sequence,
            repo.add_sequence,
            repo.back_sequence,
            repo.limit_sequence,
        ]

        for method in methods:
            with pytest.raises(HTTPException) as exc:
                await method("s1")
            assert exc.value.status_code == 404
            assert exc.value.detail == "Session not found"
