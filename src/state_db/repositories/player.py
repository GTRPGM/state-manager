from typing import Any, Dict, List

from fastapi import HTTPException

from state_db.infrastructure import run_sql_command, run_sql_query
from state_db.models import (
    FullPlayerState,
    InventoryItem,
    NPCAffinityUpdateResult,
    NPCRelation,
    PlayerHPUpdateResult,
    PlayerStateResponse,
    PlayerStats,
)
from state_db.repositories.base import BaseRepository


class PlayerRepository(BaseRepository):
    async def get_stats(self, player_id: str) -> PlayerStats:
        sql_path = self.query_dir / "INQUIRY" / "Player_stats.sql"
        result = await run_sql_query(sql_path, [player_id])
        if result:
            return PlayerStats.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Player not found")

    async def get_full_state(self, player_id: str) -> FullPlayerState:
        try:
            stats = await self.get_stats(player_id)
        except HTTPException:
            return FullPlayerState(
                player=PlayerStateResponse(hp=0, gold=0, items=[]),
                player_npc_relations=[],
            )

        relations = await self.get_npc_relations(player_id)

        # state가 dict인 경우와 객체인 경우를 모두 처리
        state_data = stats.state
        if isinstance(state_data, dict):
            numeric = state_data.get("numeric", {})
            hp = numeric.get("HP") or 0
            gold = numeric.get("gold") or 0
        else:
            hp = state_data.numeric.HP or 0
            gold = state_data.numeric.gold or 0

        return FullPlayerState(
            player=PlayerStateResponse(
                hp=hp,
                gold=gold,
                items=[],
            ),
            player_npc_relations=relations,
        )

    async def update_hp(
        self, player_id: str, session_id: str, hp_change: int
    ) -> PlayerHPUpdateResult:
        sql_path = self.query_dir / "UPDATE" / "player" / "update_player_hp.sql"
        result = await run_sql_query(sql_path, [player_id, session_id, hp_change])
        if result:
            return PlayerHPUpdateResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Player or Session not found")

    async def update_stats(
        self, player_id: str, session_id: str, stat_changes: Dict[str, int]
    ) -> PlayerStats:
        import json

        sql_path = self.query_dir / "UPDATE" / "player" / "update_player_stats.sql"
        params = [player_id, session_id, json.dumps(stat_changes)]
        await run_sql_command(sql_path, params)
        return await self.get_stats(player_id)

    async def get_inventory(self, session_id: str) -> List[InventoryItem]:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_inventory-r.sql"
        results = await run_sql_query(sql_path, [session_id])
        return [InventoryItem.model_validate(row) for row in results]

    async def update_inventory(
        self, player_id: str, item_id: int, quantity: int
    ) -> Dict[str, Any]:
        # TODO: 실제 SQL 파일 구현 필요
        return {"player_id": player_id, "item_id": item_id, "quantity": quantity}

    async def get_npc_relations(self, player_id: str) -> List[NPCRelation]:
        sql_path = self.query_dir / "INQUIRY" / "Npc_relations.sql"
        results = await run_sql_query(sql_path, [player_id])
        return [NPCRelation.model_validate(row) for row in results]

    async def update_npc_affinity(
        self, player_id: str, npc_id: str, affinity_change: int
    ) -> NPCAffinityUpdateResult:
        sql_path = self.query_dir / "UPDATE" / "update_npc_affinity-r.sql"
        result = await run_sql_query(sql_path, [player_id, npc_id, affinity_change])
        new_affinity = result[0].get("new_affinity", 0) if result else 0
        return NPCAffinityUpdateResult(
            player_id=player_id, npc_id=npc_id, new_affinity=new_affinity
        )

    async def earn_item(
        self, session_id: str, player_id: str, item_id: int, quantity: int
    ) -> Dict[str, Any]:
        sql_path = self.query_dir / "UPDATE" / "earn_item.sql"
        result = await run_sql_query(
            sql_path, [session_id, player_id, item_id, quantity]
        )
        if result:
            return result[0]
        return {"player_id": player_id, "item_id": item_id, "quantity": quantity}

    async def use_item(
        self, session_id: str, player_id: str, item_id: int, quantity: int
    ) -> Dict[str, Any]:
        sql_path = self.query_dir / "UPDATE" / "use_item.sql"
        result = await run_sql_query(
            sql_path, [session_id, player_id, item_id, quantity]
        )
        if result:
            return result[0]
        return {"player_id": player_id, "item_id": item_id, "quantity": quantity}
