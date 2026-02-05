from typing import Any, Dict, List, Union

from state_db.models import ApplyJudgmentSkipped, StateUpdateResult
from state_db.repositories import (
    EntityRepository,
    LifecycleStateRepository,
    PlayerRepository,
    SessionRepository,
)

ApplyJudgmentResult = Union[StateUpdateResult, ApplyJudgmentSkipped]


class StateService:
    def __init__(self) -> None:
        self.session_repo = SessionRepository()
        self.player_repo = PlayerRepository()
        self.entity_repo = EntityRepository()
        self.lifecycle_repo = LifecycleStateRepository()

    async def get_state_snapshot(self, session_id: str) -> Dict[str, Any]:
        session_info = await self.session_repo.get_info(session_id)
        player_id = session_info.player_id

        player_stats = None
        player_relations = []
        if player_id:
            player_stats = await self.player_repo.get_stats(player_id)
            player_relations = await self.player_repo.get_npc_relations(player_id)

        npcs = await self.entity_repo.get_session_npcs(session_id)
        enemies = await self.entity_repo.get_session_enemies(
            session_id, active_only=True
        )
        inventory = await self.player_repo.get_inventory(session_id)
        turn_info = await self.lifecycle_repo.get_turn(session_id)

        return {
            "session": session_info,
            "player": player_stats,
            "player_relations": player_relations,
            "npcs": npcs,
            "enemies": enemies,
            "inventory": inventory,
            "turn": turn_info,
            "snapshot_timestamp": session_info.updated_at,
        }

    async def write_state_changes(
        self, session_id: str, changes: Dict[str, Any]
    ) -> StateUpdateResult:
        results: List[str] = []
        player_id = changes.get("player_id")

        if "player_hp" in changes and player_id:
            await self.player_repo.update_hp(
                player_id, session_id, changes["player_hp"]
            )
            results.append("player_hp_updated")

        if "player_san" in changes and player_id:
            # SAN 업데이트 로직 추가 (세션 ID 기준)
            await self.player_repo.update_san(session_id, changes["player_san"])
            results.append("player_san_updated")

        if "player_stats" in changes and player_id:
            await self.player_repo.update_stats(
                player_id, session_id, changes["player_stats"]
            )
            results.append("player_stats_updated")

        if "enemy_hp" in changes:
            for e_id, hp_change in changes["enemy_hp"].items():
                res = await self.entity_repo.update_enemy_hp(
                    session_id, e_id, hp_change
                )
                if res.current_hp <= 0:
                    await self.entity_repo.defeat_enemy(session_id, e_id)
            results.append("enemy_hp_updated")

        if "npc_affinity" in changes and player_id:
            for npc_id, aff_change in changes["npc_affinity"].items():
                await self.player_repo.update_npc_affinity(
                    player_id, npc_id, aff_change
                )
            results.append("npc_affinity_updated")

        if "location" in changes:
            await self.session_repo.update_location(session_id, changes["location"])
            results.append("location_updated")

        if changes.get("turn_increment", False):
            await self.lifecycle_repo.add_turn(session_id)
            results.append("turn_incremented")

        if "act" in changes:
            await self.session_repo.change_act(session_id, changes["act"])
            results.append("act_updated")

        if "sequence" in changes:
            await self.session_repo.change_sequence(session_id, changes["sequence"])
            results.append("sequence_updated")

        return StateUpdateResult(
            status="success",
            message=f"State updated: {', '.join(results)}",
            updated_fields=results,
        )

    async def process_combat_end(
        self, session_id: str, victory: bool
    ) -> Dict[str, Any]:
        changes = {}
        if victory:
            enemies = await self.entity_repo.get_session_enemies(
                session_id, active_only=True
            )
            for enemy in enemies:
                await self.entity_repo.remove_enemy(session_id, enemy.enemy_instance_id)

        result = await self.write_state_changes(session_id, changes)
        return {"status": "success", "victory": victory, "result": result}
