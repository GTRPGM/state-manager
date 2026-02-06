from typing import Any, Dict, List, Optional, Union

from state_db.models import ApplyJudgmentSkipped, StateUpdateResult
from state_db.repositories import (
    EntityRepository,
    LifecycleStateRepository,
    PlayerRepository,
    ProgressRepository,
    ScenarioRepository,
    SessionRepository,
)

ApplyJudgmentResult = Union[StateUpdateResult, ApplyJudgmentSkipped]


class StateService:
    def __init__(self) -> None:
        self.session_repo = SessionRepository()
        self.player_repo = PlayerRepository()
        self.entity_repo = EntityRepository()
        self.lifecycle_repo = LifecycleStateRepository()
        self.progress_repo = ProgressRepository()
        self.scenario_repo = ScenarioRepository()

    async def get_state_snapshot(
        self,
        session_id: str,
        sequence_id: Optional[str] = None,
        include_inactive: bool = False,
    ) -> Dict[str, Any]:
        def _entity_id(row: Any) -> str:
            if isinstance(row, dict):
                return str(
                    row.get("id") or row.get("npc_id") or row.get("enemy_id") or ""
                )
            return str(
                getattr(row, "id", None)
                or getattr(row, "npc_id", None)
                or getattr(row, "enemy_id", None)
                or ""
            )

        session_info = await self.session_repo.get_info(session_id)
        player_id = session_info.player_id

        player_stats = None
        graph_context = {"items": [], "npcs": []}
        relations = []
        player_relations = []
        npcs: List[Dict[str, Any]] = []
        enemies: List[Dict[str, Any]] = []

        if player_id:
            player_stats = await self.player_repo.get_stats(player_id)
            # Cypher 기반 통합 컨텍스트 조회 (Inventory, Relations, Enemies)
            graph_context = await self.player_repo.get_full_context(
                session_id, include_inactive=include_inactive
            )
            player_relations = graph_context.get("npcs", [])

        # 세션 전체 엔티티 목록은 엔티티 리포지토리 기준으로 조회
        active_only = not include_inactive
        npcs = [
            npc.model_dump(mode="json")
            for npc in await self.entity_repo.get_session_npcs(
                session_id, active_only=active_only
            )
        ]
        enemies = [
            enemy.model_dump(mode="json")
            for enemy in await self.entity_repo.get_session_enemies(
                session_id, active_only=active_only
            )
        ]

        # 전체 관계(Edge) 조회
        relations = await self.entity_repo.get_all_relations(session_id)
        resolved_sequence_id = sequence_id or getattr(
            session_info, "current_sequence_id", None
        )

        if resolved_sequence_id:
            ids = await self.scenario_repo.get_sequence_entity_ids(
                session_id, resolved_sequence_id
            )
            npc_ids = set(ids.get("npc_ids", []))
            enemy_ids = set(ids.get("enemy_ids", []))

            npcs = [npc for npc in npcs if _entity_id(npc) in npc_ids]
            enemies = [enemy for enemy in enemies if _entity_id(enemy) in enemy_ids]

            # 시퀀스 단위 world snapshot에서는 관련 엔티티 관계만 남긴다.
            allowed_ids = npc_ids.union(enemy_ids)
            relations = [
                rel
                for rel in relations
                if str(rel.from_id) in allowed_ids and str(rel.to_id) in allowed_ids
            ]

        turn_info = await self.lifecycle_repo.get_turn(session_id)

        return {
            "session": session_info,
            "player": player_stats,
            "player_relations": player_relations,
            "npcs": npcs,
            "enemies": enemies,
            "inventory": graph_context.get("items", []),
            "relations": relations,
            "context_scope": {
                "sequence_id": resolved_sequence_id,
                "include_inactive": include_inactive,
            },
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

        if "relation_updates" in changes:
            turn_info = await self.lifecycle_repo.get_turn(session_id)
            current_turn = int(getattr(turn_info, "current_turn", 0))
            for rel in changes["relation_updates"]:
                await self.entity_repo.upsert_relation(
                    session_id=session_id,
                    cause_entity_id=str(rel.get("cause_entity_id", "")),
                    effect_entity_id=str(rel.get("effect_entity_id", "")),
                    relation_type=str(rel.get("type", "neutral")),
                    affinity_score=rel.get("affinity_score"),
                    quantity=rel.get("quantity"),
                    turn=current_turn,
                )
            results.append("relations_updated")

        if "location" in changes:
            await self.progress_repo.update_location(session_id, changes["location"])
            results.append("location_updated")

        if changes.get("turn_increment", False):
            await self.lifecycle_repo.add_turn(session_id)
            results.append("turn_incremented")

        if "act" in changes:
            await self.progress_repo.change_act(session_id, int(changes["act"]))
            results.append("act_updated")

        if "sequence" in changes:
            await self.progress_repo.change_sequence(
                session_id, int(changes["sequence"])
            )
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
                await self.entity_repo.remove_enemy(session_id, enemy.enemy_id)

        result = await self.write_state_changes(session_id, changes)
        return {"status": "success", "victory": victory, "result": result}
