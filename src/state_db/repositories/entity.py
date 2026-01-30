from typing import Any, Dict, List

from fastapi import HTTPException

from state_db.infrastructure import run_sql_command, run_sql_query
from state_db.models import (
    EnemyHPUpdateResult,
    EnemyInfo,
    ItemInfo,
    NPCInfo,
    RemoveEntityResult,
    SpawnResult,
)
from state_db.repositories.base import BaseRepository


class EntityRepository(BaseRepository):
    # Item
    async def get_session_items(self, session_id: str) -> List[ItemInfo]:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_item.sql"
        results = await run_sql_query(sql_path, [session_id])
        return [ItemInfo.model_validate(row) for row in results]

    # NPC
    async def get_session_npcs(self, session_id: str) -> List[NPCInfo]:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_npc.sql"
        results = await run_sql_query(sql_path, [session_id])
        return [NPCInfo.model_validate(row) for row in results]

    async def spawn_npc(self, session_id: str, data: Dict[str, Any]) -> SpawnResult:
        sql_path = self.query_dir / "MANAGE" / "npc" / "spawn_npc.sql"
        params = [
            session_id,
            data.get("npc_id"),
            data.get("name"),
            data.get("description", ""),
            data.get("hp", 100),
            data.get("tags", ["npc"]),
        ]
        result = await run_sql_query(sql_path, params)
        if result:
            return SpawnResult(
                id=result[0].get("id", ""), name=result[0].get("name", "")
            )
        raise HTTPException(status_code=500, detail="Failed to spawn NPC")

    async def remove_npc(
        self, session_id: str, npc_instance_id: str
    ) -> RemoveEntityResult:
        sql_path = self.query_dir / "MANAGE" / "npc" / "remove_npc.sql"
        await run_sql_command(sql_path, [npc_instance_id, session_id])
        return RemoveEntityResult()

    # Enemy
    async def get_session_enemies(
        self, session_id: str, active_only: bool = True
    ) -> List[EnemyInfo]:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_enemy.sql"
        results = await run_sql_query(sql_path, [session_id, active_only])
        return [EnemyInfo.model_validate(row) for row in results]

    async def spawn_enemy(self, session_id: str, data: Dict[str, Any]) -> SpawnResult:
        sql_path = self.query_dir / "MANAGE" / "enemy" / "spawn_enemy.sql"
        params = [
            session_id,
            data.get("enemy_id"),
            data.get("name"),
            data.get("description", ""),
            data.get("hp", 30),
            data.get("attack", 10),
            data.get("defense", 5),
            data.get("tags", ["enemy"]),
        ]
        result = await run_sql_query(sql_path, params)
        if result:
            return SpawnResult(
                id=result[0].get("id", ""),
                name=result[0].get("name", ""),
            )
        raise HTTPException(status_code=500, detail="Failed to spawn enemy")

    async def update_enemy_hp(
        self, session_id: str, enemy_instance_id: str, hp_change: int
    ) -> EnemyHPUpdateResult:
        sql_path = self.query_dir / "UPDATE" / "enemy" / "update_enemy_hp.sql"
        result = await run_sql_query(
            sql_path, [enemy_instance_id, session_id, hp_change]
        )
        if result:
            # SQL에서 반환하는 필드명과 모델 필드명이 일치해야 함
            return EnemyHPUpdateResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Enemy or Session not found")

    async def remove_enemy(
        self, session_id: str, enemy_instance_id: str
    ) -> RemoveEntityResult:
        sql_path = self.query_dir / "MANAGE" / "enemy" / "remove_enemy.sql"
        await run_sql_command(sql_path, [enemy_instance_id, session_id])
        return RemoveEntityResult()

    async def defeat_enemy(self, session_id: str, enemy_instance_id: str) -> None:
        sql_path = self.query_dir / "UPDATE" / "defeated_enemy.sql"
        await run_sql_command(sql_path, [enemy_instance_id, session_id])
