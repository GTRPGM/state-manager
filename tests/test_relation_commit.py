import pytest
from unittest.mock import AsyncMock, patch
from state_db.routers.router_COMMIT import state_commit
from state_db.schemas.requests import CommitRequest, CommitUpdate, RelationDiff

@pytest.mark.asyncio
async def test_state_commit_handles_npc_relations():
    # Setup
    mock_service = AsyncMock()
    mock_service.session_repo.get_info.return_value = AsyncMock(player_id="player-123")
    mock_service.write_state_changes.return_value = AsyncMock(
        updated_fields=["relations_updated"],
        message="Success"
    )

    request = CommitRequest(
        turn_id="session-1:1",
        update=CommitUpdate(
            diffs=[],
            relations=[
                RelationDiff(
                    cause_entity_id="player-123",
                    effect_entity_id="npc-456",
                    type="NEUTRAL",
                    affinity_score=10
                )
            ]
        )
    )

    # Execute
    response = await state_commit(request, mock_service)

    # Verify
    assert response["status"] == "success"
    
    # Check if write_state_changes was called with correct structure
    mock_service.write_state_changes.assert_called_once()
    call_args = mock_service.write_state_changes.call_args
    session_id = call_args[0][0]
    changes = call_args[0][1]

    assert session_id == "session-1"
    assert "relation_updates" in changes
    relations = changes["relation_updates"]
    assert len(relations) == 1
    assert relations[0]["cause_entity_id"] == "player-123"
    assert relations[0]["effect_entity_id"] == "npc-456"
    assert relations[0]["type"] == "NEUTRAL"
    assert relations[0]["affinity_score"] == 10
