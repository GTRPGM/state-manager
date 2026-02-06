from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_commit_accepts_wrapped_rule_engine_update(async_client: AsyncClient):
    session_id = "00000000-0000-0000-0000-000000000010"
    mock_write_state_changes = AsyncMock(
        return_value=type(
            "CommitResult",
            (),
            {
                "updated_fields": ["player_hp_updated", "relations_updated"],
                "message": "State updated",
            },
        )()
    )

    payload = {
        "turn_id": f"{session_id}:12",
        "update": {
            "diffs": [
                {
                    "state_entity_id": "player",
                    "diff": {"hp": -5, "location": "market"},
                }
            ],
            "relations": [
                {
                    "cause_entity_id": "npc-1",
                    "effect_entity_id": "enemy-1",
                    "type": "적대적",
                    "affinity_score": -20,
                }
            ],
        },
    }

    with (
        patch(
            "state_db.repositories.SessionRepository.get_info",
            new=AsyncMock(
                return_value=type(
                    "SessionInfo",
                    (),
                    {"player_id": "00000000-0000-0000-0000-000000000099"},
                )()
            ),
        ),
        patch(
            "state_db.services.state_service.StateService.write_state_changes",
            new=mock_write_state_changes,
        ),
    ):
        response = await async_client.post("/state/commit", json=payload)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["updated_fields"] == ["player_hp_updated", "relations_updated"]

    mock_write_state_changes.assert_awaited_once()
    called_session_id, called_changes = mock_write_state_changes.await_args.args
    assert called_session_id == session_id
    assert called_changes["player_hp"] == -5
    assert called_changes["location"] == "market"
    assert len(called_changes["relation_updates"]) == 1
    assert called_changes["relation_updates"][0]["type"] == "적대적"


@pytest.mark.asyncio
async def test_commit_invalid_turn_id_returns_400(async_client: AsyncClient):
    payload = {"turn_id": ":1", "update": {"diffs": [], "relations": []}}
    response = await async_client.post("/state/commit", json=payload)
    assert response.status_code == 400
