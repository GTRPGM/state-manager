from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from state_db.services.state_service import StateService


class _Dumpable:
    def __init__(self, payload):
        self._payload = payload

    def model_dump(self, mode="json"):
        return self._payload


@pytest.mark.asyncio
async def test_get_state_snapshot_filters_by_sequence():
    svc = StateService()
    svc.session_repo = SimpleNamespace(
        get_info=AsyncMock(
            return_value=SimpleNamespace(
                player_id="p1",
                current_sequence_id="seq-1",
                updated_at="2026-02-08T00:00:00Z",
            )
        )
    )
    svc.player_repo = SimpleNamespace(
        get_stats=AsyncMock(return_value={"hp": 100}),
        get_full_context=AsyncMock(
            return_value={"items": [{"id": "it-1"}], "npcs": [{"npc_id": "npc-1"}]}
        ),
    )
    svc.entity_repo = SimpleNamespace(
        get_session_npcs=AsyncMock(
            return_value=[
                _Dumpable({"id": "npc-1", "name": "A"}),
                _Dumpable({"id": "npc-2", "name": "B"}),
            ]
        ),
        get_session_enemies=AsyncMock(
            return_value=[
                _Dumpable({"enemy_id": "enemy-1", "name": "E1"}),
                _Dumpable({"enemy_id": "enemy-2", "name": "E2"}),
            ]
        ),
        get_all_relations=AsyncMock(
            return_value=[
                SimpleNamespace(from_id="npc-1", to_id="enemy-1"),
                SimpleNamespace(from_id="npc-2", to_id="enemy-2"),
            ]
        ),
    )
    svc.scenario_repo = SimpleNamespace(
        get_sequence_entity_ids=AsyncMock(
            return_value={"npc_ids": ["npc-1"], "enemy_ids": ["enemy-1"]}
        )
    )
    svc.lifecycle_repo = SimpleNamespace(get_turn=AsyncMock(return_value={"turn": 2}))

    snapshot = await svc.get_state_snapshot("s1")

    assert snapshot["player"] == {"hp": 100}
    assert snapshot["inventory"] == [{"id": "it-1"}]
    assert snapshot["context_scope"]["sequence_id"] == "seq-1"
    assert len(snapshot["npcs"]) == 1
    assert snapshot["npcs"][0]["id"] == "npc-1"
    assert len(snapshot["enemies"]) == 1
    assert snapshot["enemies"][0]["enemy_id"] == "enemy-1"
    assert len(snapshot["relations"]) == 1
    assert snapshot["snapshot_timestamp"] == "2026-02-08T00:00:00Z"


@pytest.mark.asyncio
async def test_write_state_changes_covers_all_branches():
    svc = StateService()
    svc.player_repo = SimpleNamespace(
        update_hp=AsyncMock(),
        update_san=AsyncMock(),
        update_stats=AsyncMock(),
        update_npc_affinity=AsyncMock(),
    )
    svc.entity_repo = SimpleNamespace(
        update_enemy_hp=AsyncMock(
            side_effect=[
                SimpleNamespace(current_hp=0),
                SimpleNamespace(current_hp=5),
            ]
        ),
        defeat_enemy=AsyncMock(),
        upsert_relation=AsyncMock(),
    )
    svc.lifecycle_repo = SimpleNamespace(
        get_turn=AsyncMock(return_value=SimpleNamespace(current_turn=7)),
        add_turn=AsyncMock(),
    )
    svc.progress_repo = SimpleNamespace(
        update_location=AsyncMock(),
        change_act=AsyncMock(),
        change_sequence=AsyncMock(),
    )

    result = await svc.write_state_changes(
        "s1",
        {
            "player_id": "p1",
            "player_hp": -10,
            "player_san": -1,
            "player_stats": {"hp": 90},
            "enemy_hp": {"enemy-1": -9, "enemy-2": -3},
            "npc_affinity": {"npc-1": 1},
            "relation_updates": [
                {
                    "cause_entity_id": "npc-1",
                    "effect_entity_id": "enemy-1",
                    "type": "hostile",
                    "affinity_score": -5,
                    "quantity": 1,
                }
            ],
            "location": "forest",
            "turn_increment": True,
            "act": 2,
            "sequence": 3,
        },
    )

    assert result.status == "success"
    assert set(result.updated_fields) == {
        "player_hp_updated",
        "player_san_updated",
        "player_stats_updated",
        "enemy_hp_updated",
        "npc_affinity_updated",
        "relations_updated",
        "location_updated",
        "turn_incremented",
        "act_updated",
        "sequence_updated",
    }
    svc.entity_repo.defeat_enemy.assert_awaited_once_with("s1", "enemy-1")


@pytest.mark.asyncio
async def test_process_combat_end_victory_and_non_victory():
    svc = StateService()
    svc.entity_repo = SimpleNamespace(
        get_session_enemies=AsyncMock(
            return_value=[
                SimpleNamespace(enemy_id="enemy-1"),
                SimpleNamespace(enemy_id="enemy-2"),
            ]
        ),
        remove_enemy=AsyncMock(),
    )
    svc.write_state_changes = AsyncMock(return_value={"status": "success"})

    win = await svc.process_combat_end("s1", victory=True)
    lose = await svc.process_combat_end("s1", victory=False)

    assert win["status"] == "success"
    assert win["victory"] is True
    assert lose["victory"] is False
    assert svc.entity_repo.remove_enemy.await_count == 2
