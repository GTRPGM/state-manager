from unittest.mock import AsyncMock, patch

import pytest

from state_db.pipeline import (
    StateUpdateResult,
    apply_rule_judgment,
    process_action,
    write_state_snapshot,
)
from state_db.Query import PhaseChangeResult

# Mock data
MOCK_SESSION_ID = "test-session-id"
MOCK_PLAYER_ID = "test-player-id"


@pytest.mark.asyncio
async def test_process_action_combat():
    # Mock dependencies
    mock_phase_info = PhaseChangeResult(
        session_id=MOCK_SESSION_ID, current_phase="combat"
    )
    mock_judgment = {
        "success": True,
        "action_type": "attack",
        "result": "Success",
        "state_changes": {"player_hp": -5},
    }
    mock_final_state = {"player": {"hp": 95}}
    mock_apply_result = StateUpdateResult(
        status="success", message="State updated", updated_fields=["player_hp"]
    )

    with (
        patch(
            "state_db.pipeline.get_current_phase",
            new=AsyncMock(return_value=mock_phase_info),
        ),
        patch(
            "state_db.pipeline.request_rule_judgment",
            new=AsyncMock(return_value=mock_judgment),
        ) as mock_req_rule,
        patch(
            "state_db.pipeline.apply_rule_judgment",
            new=AsyncMock(return_value=mock_apply_result),
        ) as mock_apply,
        patch(
            "state_db.pipeline.get_state_snapshot",
            new=AsyncMock(return_value=mock_final_state),
        ),
    ):
        action = {"action_type": "attack", "target": "enemy-1"}
        result = await process_action(MOCK_SESSION_ID, MOCK_PLAYER_ID, action)

        assert result["status"] == "success"
        assert result["judgment"] == mock_judgment
        assert result["final_state"] == mock_final_state

        mock_req_rule.assert_called_once()
        mock_apply.assert_called_once_with(MOCK_SESSION_ID, mock_judgment)


@pytest.mark.asyncio
async def test_process_action_unknown_phase():
    mock_phase_info = PhaseChangeResult(
        session_id=MOCK_SESSION_ID, current_phase="unknown_phase"
    )

    with patch(
        "state_db.pipeline.get_current_phase",
        new=AsyncMock(return_value=mock_phase_info),
    ):
        action = {"action_type": "test"}
        result = await process_action(MOCK_SESSION_ID, MOCK_PLAYER_ID, action)

        assert result["status"] == "error"
        assert "Unknown phase" in result["message"]


@pytest.mark.asyncio
async def test_apply_rule_judgment_success():
    judgment = {
        "success": True,
        "state_changes": {"player_hp": -10, "turn_increment": True},
    }
    mock_write_result = StateUpdateResult(
        status="success", message="State updated", updated_fields=["player_hp", "turn"]
    )

    with patch(
        "state_db.pipeline.write_state_snapshot",
        new=AsyncMock(return_value=mock_write_result),
    ) as mock_write:
        result = await apply_rule_judgment(MOCK_SESSION_ID, judgment)

        assert result == mock_write_result
        mock_write.assert_called_once_with(MOCK_SESSION_ID, judgment["state_changes"])


@pytest.mark.asyncio
async def test_apply_rule_judgment_failure():
    judgment = {"success": False}

    result = await apply_rule_judgment(MOCK_SESSION_ID, judgment)

    assert result.status == "skipped"
    assert "Judgment failed" in result.message


@pytest.mark.asyncio
async def test_write_state_snapshot():
    # Test that write_state_snapshot calls appropriate update functions
    state_changes = {
        "player_id": MOCK_PLAYER_ID,
        "player_hp": -10,
        "location": "New Town",
        "turn_increment": True,
    }

    with (
        patch("state_db.pipeline.update_player_hp", new=AsyncMock()) as mock_hp,
        patch("state_db.pipeline.update_location", new=AsyncMock()) as mock_loc,
        patch("state_db.pipeline.add_turn", new=AsyncMock()) as mock_turn,
    ):
        result = await write_state_snapshot(MOCK_SESSION_ID, state_changes)

        assert result.status == "success"

        mock_hp.assert_called_once()
        mock_loc.assert_called_once()
        mock_turn.assert_called_once()
