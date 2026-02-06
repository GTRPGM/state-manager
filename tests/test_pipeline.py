from unittest.mock import AsyncMock, patch

import pytest

import state_db.pipeline as pipeline
from state_db.models import StateUpdateResult

# Mock data
MOCK_SESSION_ID = "test-session-id"
MOCK_PLAYER_ID = "test-player-id"


@pytest.mark.asyncio
async def test_process_action_success():
    mock_final_state = {"player": {"hp": 95}}

    with (
        patch(
            "state_db.pipeline.get_state_snapshot",
            new=AsyncMock(return_value=mock_final_state),
        ),
    ):
        action = {"action_type": "attack", "target": "enemy-1"}
        result = await pipeline.process_action(MOCK_SESSION_ID, MOCK_PLAYER_ID, action)

        assert result["status"] == "success"
        assert result["initial_state"] == mock_final_state


@pytest.mark.asyncio
async def test_write_state_snapshot():
    state_changes = {
        "player_id": MOCK_PLAYER_ID,
        "player_hp": -10,
        "location": "New Town",
        "turn_increment": True,
    }

    mock_result = StateUpdateResult(
        status="success", message="updated", updated_fields=["hp"]
    )

    # Patch the service method called by pipeline.write_state_snapshot
    with patch(
        "state_db.pipeline._service.write_state_changes",
        new=AsyncMock(return_value=mock_result),
    ) as mock_write:
        result = await pipeline.write_state_snapshot(MOCK_SESSION_ID, state_changes)
        assert result.status == "success"
        mock_write.assert_called_once_with(MOCK_SESSION_ID, state_changes)
