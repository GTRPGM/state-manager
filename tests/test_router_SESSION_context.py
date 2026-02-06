from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_session_context_accepts_sequence_query_params(async_client: AsyncClient):
    session_id = "00000000-0000-0000-0000-000000000111"
    mocked_snapshot = {
        "session": {"session_id": session_id},
        "player": {"hp": 100},
        "npcs": [],
        "enemies": [],
        "inventory": [],
        "relations": [],
        "context_scope": {
            "sequence_id": "seq-1",
            "include_inactive": False,
        },
    }

    with patch(
        "state_db.services.state_service.StateService.get_state_snapshot",
        new=AsyncMock(return_value=mocked_snapshot),
    ) as mocked_get_snapshot:
        response = await async_client.get(
            f"/state/session/{session_id}/context",
            params={"sequence_id": "seq-1", "include_inactive": "false"},
        )

    assert response.status_code == 200
    assert response.json()["data"]["context_scope"]["sequence_id"] == "seq-1"
    mocked_get_snapshot.assert_awaited_once_with(
        session_id=session_id,
        sequence_id="seq-1",
        include_inactive=False,
    )
