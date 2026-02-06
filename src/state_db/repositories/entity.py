from typing import Any, Dict, List

from fastapi import HTTPException

from state_db.graph.cypher_engine import engine as cypher_engine
from state_db.infrastructure import (
    run_raw_query,
    run_sql_command,
    run_sql_query,
)
from state_db.models import (
    EnemyHPUpdateResult,
    EnemyInfo,
    ItemInfo,
    NPCDepartResult,
    NPCInfo,
    NPCReturnResult,
    RemoveEntityResult,
    SpawnResult,
)
from state_db.repositories.base import BaseRepository


class EntityRepository(BaseRepository):
    """
    엔티티의 생명주기 및 조회를 담당하는 리포지토리.
    원칙: 관계는 그래프(Cypher), 상태는 테이블(SQL).
    """

    # Item
    async def get_session_items(self, session_id: str) -> List[ItemInfo]:
        # 1. 그래프에서 아이템 ID 리스트 조회
        cypher_path = str(
            self.query_dir / "CYPHER" / "inquiry" / "get_session_items.cypher"
        )
        results = await cypher_engine.run_cypher(
            cypher_path, {"session_id": session_id}
        )
        # AGE 문자열의 따옴표 제거 후 UUID 리스트로 정규화
        item_ids = [str(row).strip('"') for row in results if row]
        if not item_ids:
            return []

        # 2. SQL 테이블에서 상세 정보 결합
        query = """
            SELECT
                item_id, scenario_item_id, rule_id,
                name, description, item_type, meta
            FROM item
            WHERE item_id = ANY($1::uuid[])
        """
        rows = await run_raw_query(query, [item_ids])
        return [ItemInfo.model_validate(row) for row in rows]

    # NPC
    async def get_session_npcs(
        self, session_id: str, active_only: bool = True
    ) -> List[NPCInfo]:
        # 1. 그래프에서 NPC ID 리스트 조회 (관계/활성화 기준)
        cypher_path = str(
            self.query_dir / "CYPHER" / "inquiry" / "get_session_npcs.cypher"
        )
        results = await cypher_engine.run_cypher(
            cypher_path, {"session_id": session_id, "active_only": active_only}
        )
        # AGE 결과에서 'id' 필드 추출 및 UUID 정규화
        npc_ids = []
        for row in results:
            if isinstance(row, dict):
                val = row.get("id")
            else:
                val = row
            if val:
                npc_ids.append(str(val).strip('"'))

        if not npc_ids:
            return []

        # 2. SQL 테이블에서 상세 상태 결합
        query = """
            SELECT
                npc_id, scenario_npc_id, rule_id, name, description,
                hp as current_hp,
                tags, assigned_sequence_id, assigned_location,
                is_departed, mp, str, dex, int, lux, san
            FROM npc
            WHERE npc_id = ANY($1::uuid[])
        """
        rows = await run_raw_query(query, [npc_ids])
        return [NPCInfo.model_validate(row) for row in rows]

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
        # SQL 삭제 (트리거가 없으므로 명시적 삭제)
        sql_path = self.query_dir / "MANAGE" / "npc" / "remove_npc.sql"
        await run_sql_command(sql_path, [npc_instance_id, session_id])

        # Graph 노드 삭제
        cypher_path = str(
            self.query_dir / "CYPHER" / "entity" / "npc" / "remove_npc.cypher"
        )
        await cypher_engine.run_cypher(
            cypher_path, {"npc_id": npc_instance_id, "session_id": session_id}
        )
        return RemoveEntityResult()

    async def depart_npc(self, session_id: str, npc_id: str) -> NPCDepartResult:
        """NPC 퇴장 처리 (SQL Truth 업데이트 -> 트리거 동기화)"""
        sql_path = self.query_dir / "MANAGE" / "npc" / "depart_npc.sql"
        result = await run_sql_query(sql_path, [npc_id, session_id])
        if result:
            return NPCDepartResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="NPC not found or already departed")

    async def return_npc(self, session_id: str, npc_id: str) -> NPCReturnResult:
        """퇴장한 NPC 복귀 처리 (SQL Truth 업데이트)"""
        sql_path = self.query_dir / "MANAGE" / "npc" / "return_npc.sql"
        result = await run_sql_query(sql_path, [npc_id, session_id])
        if result:
            return NPCReturnResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="NPC not found or not departed")

    # Enemy
    async def get_session_enemies(
        self, session_id: str, active_only: bool = True
    ) -> List[EnemyInfo]:
        # 1. 그래프에서 적 ID 리스트 조회
        cypher_path = str(
            self.query_dir / "CYPHER" / "inquiry" / "get_session_enemies.cypher"
        )
        results = await cypher_engine.run_cypher(
            cypher_path, {"session_id": session_id, "active_only": active_only}
        )
        # AGE 결과에서 'id' 필드 추출 및 UUID 정규화
        enemy_ids = []
        for row in results:
            if isinstance(row, dict):
                val = row.get("id")
            else:
                val = row
            if val:
                enemy_ids.append(str(val).strip('"'))

        if not enemy_ids:
            return []

        # 2. SQL 테이블에서 상세 상태 결합
        query = """
            SELECT
                enemy_id, scenario_enemy_id, rule_id, name, description,
                hp as current_hp,
                tags, assigned_sequence_id, assigned_location,
                is_defeated, max_hp, attack, defense, dropped_items
            FROM enemy
            WHERE enemy_id = ANY($1::uuid[])
        """
        rows = await run_raw_query(query, [enemy_ids])
        return [EnemyInfo.model_validate(row) for row in rows]

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
            return EnemyHPUpdateResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Enemy or Session not found")

    async def remove_enemy(
        self, session_id: str, enemy_instance_id: str
    ) -> RemoveEntityResult:
        # SQL 삭제
        sql_path = self.query_dir / "MANAGE" / "enemy" / "remove_enemy.sql"
        await run_sql_command(sql_path, [enemy_instance_id, session_id])

        # Graph 삭제
        cypher_path = str(
            self.query_dir / "CYPHER" / "entity" / "enemy" / "remove_enemy.cypher"
        )
        await cypher_engine.run_cypher(
            cypher_path,
            {"enemy_id": enemy_instance_id, "session_id": session_id},
        )
        return RemoveEntityResult()

    async def defeat_enemy(self, session_id: str, enemy_instance_id: str) -> None:
        sql_path = self.query_dir / "UPDATE" / "defeated_enemy.sql"
        await run_sql_command(sql_path, [enemy_instance_id, session_id])
