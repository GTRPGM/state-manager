from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException

from state_db.graph.cypher_engine import engine as cypher_engine
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

    async def get_item_ids(self, player_id: str) -> List[int]:
        """플레이어가 보유한 아이템 Rule ID 리스트 조회 (Cypher 기반)"""
        # session_id 조회를 위해 SQL 활용
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_player.sql"
        rows = await run_sql_query(sql_path, [player_id])
        if not rows:
            return []
        session_id = str(rows[0].get("session_id", ""))

        cypher_path = str(
            self.query_dir / "CYPHER" / "inquiry" / "get_inventory.cypher"
        )
        results = await cypher_engine.run_cypher(
            cypher_path, {"player_id": player_id, "session_id": session_id}
        )

        return [row.get("rule_id", 0) for row in results if row]

    async def get_full_state(self, player_id: str) -> FullPlayerState:
        try:
            stats = await self.get_stats(player_id)
        except HTTPException:
            return FullPlayerState(
                player=PlayerStateResponse(hp=0, gold=0, items=[]),
                player_npc_relations=[],
            )

        relations = await self.get_npc_relations(player_id)
        item_ids = await self.get_item_ids(player_id)

        return FullPlayerState(
            player=PlayerStateResponse(
                hp=stats.hp,
                gold=0,  # gold는 현재 스키마에 없으므로 0 기본값
                items=item_ids,
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

    async def get_full_context(
        self, session_id: str, include_inactive: bool = False
    ) -> Dict[str, Any]:
        """세션의 전체 컨텍스트(인벤토리 + 관계)를 한 번에 조회 (Cypher 기반)"""
        # session에서 player_id 조회
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_player.sql"
        rows = await run_sql_query(sql_path, [session_id])
        if not rows:
            return {"items": [], "npcs": []}
        player_id = str(rows[0].get("player_id", ""))

        cypher_path = str(self.query_dir / "CYPHER" / "inquiry" / "context.cypher")
        params = {
            "player_id": player_id,
            "session_id": session_id,
            "include_inactive": include_inactive,
        }

        results = await cypher_engine.run_cypher(cypher_path, params)

        if results and results[0]:
            # ResultMapper에 의해 파싱된 dict 반환
            return results[0]

        return {"items": [], "npcs": []}

    async def get_inventory(self, session_id: str) -> List[InventoryItem]:
        """플레이어 인벤토리 조회 (Cypher 기반)"""
        # session에서 player_id 조회
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_player.sql"
        rows = await run_sql_query(sql_path, [session_id])
        if not rows:
            return []
        player_id = str(rows[0].get("player_id", ""))
        if not player_id:
            return []

        cypher_path = str(
            self.query_dir / "CYPHER" / "inquiry" / "get_inventory.cypher"
        )
        results = await cypher_engine.run_cypher(
            cypher_path, {"player_id": player_id, "session_id": session_id}
        )

        inventory_items = []
        for row in results:
            if row and isinstance(row, dict):
                props = row.get("properties", row)
                inventory_items.append(
                    InventoryItem(
                        player_id=props.get("player_id", player_id),
                        item_id=props.get("item_id", ""),
                        rule_id=props.get("rule_id", 0),
                        item_name=props.get("item_name"),
                        description=props.get("description"),
                        quantity=props.get("quantity", 0),
                        active=props.get("active", True),
                        activated_turn=props.get("activated_turn", 0),
                        deactivated_turn=props.get("deactivated_turn"),
                    )
                )
        return inventory_items

    async def update_inventory(
        self, player_id: str, item_id: int, quantity: int
    ) -> Dict[str, Any]:
        sql_path = self.query_dir / "UPDATE" / "inventory" / "update_inventory.sql"
        result = await run_sql_query(sql_path, [player_id, item_id, quantity])
        if result:
            return result[0]
        return {"player_id": player_id, "item_id": item_id, "quantity": quantity}

    async def get_npc_relations(
        self, player_id: str, session_id: Optional[str] = None
    ) -> List[NPCRelation]:
        """NPC 관계 조회 (Cypher 기반)"""
        # session_id가 없으면 player_id로 조회
        if not session_id:
            sql_path = self.query_dir / "INQUIRY" / "session" / "Session_player.sql"
            rows = await run_sql_query(sql_path, [player_id])
            if rows:
                session_id = str(rows[0].get("session_id", ""))
            else:
                return []

        cypher_path = str(
            self.query_dir / "CYPHER" / "relation" / "get_relations.cypher"
        )
        results = await cypher_engine.run_cypher(
            cypher_path, {"player_id": player_id, "session_id": session_id}
        )

        relations = []
        for row in results:
            if row and isinstance(row, dict):
                # ResultMapper가 {"__age_type__": ..., "value": ...} 형태로 반환
                props = row.get("properties", row)
                relations.append(
                    NPCRelation(
                        npc_id=props.get("npc_id", props.get("value", "")),
                        npc_name=props.get("npc_name"),
                        affinity_score=props.get("affinity_score", 0),
                        active=props.get("active", True),
                        activated_turn=props.get("activated_turn", 0),
                        deactivated_turn=props.get("deactivated_turn"),
                        relation_type=props.get("relation_type", "neutral"),
                    )
                )
        return relations

    async def update_npc_affinity(
        self,
        player_id: str,
        npc_id: str,
        affinity_change: int,
        session_id: Optional[str] = None,
        relation_type: str = "neutral",
    ) -> NPCAffinityUpdateResult:
        """NPC 호감도 업데이트 (Cypher 기반, delta 방식)

        Args:
            affinity_change: 호감도 변동값 (예: +3, -2). 결과는 0~100 범위로 제한됨
        """
        # session_id가 없으면 player_id로 조회
        if not session_id:
            sql_path = self.query_dir / "INQUIRY" / "session" / "Session_player.sql"
            rows = await run_sql_query(sql_path, [player_id])
            if rows:
                session_id = str(rows[0].get("session_id", ""))
                current_turn = rows[0].get("current_turn", 0)
            else:
                raise HTTPException(status_code=404, detail="Player session not found")
        else:
            # session_id가 있으면 current_turn만 조회
            turn_sql = self.query_dir / "INQUIRY" / "session" / "Session_turn.sql"
            turn_rows = await run_sql_query(turn_sql, [session_id])
            current_turn = turn_rows[0].get("current_turn", 0) if turn_rows else 0

        # NPC context 조회 (scenario, rule)
        npc_ctx = await self._get_npc_context(npc_id, session_id)

        cypher_path = str(self.query_dir / "CYPHER" / "relation" / "relation.cypher")
        params = {
            "player_id": player_id,
            "session_id": session_id,
            "npc_uuid": npc_id,
            "scenario": npc_ctx.get("scenario", ""),
            "rule": npc_ctx.get("rule", 0),
            "relation_type": relation_type,
            "delta_affinity": affinity_change,
            "turn": current_turn,
            "meta_json": "{}",
        }

        results = await cypher_engine.run_cypher(cypher_path, params)

        new_affinity = 0
        if results and results[0]:
            val = results[0]
            if isinstance(val, dict):
                new_affinity = val.get("affinity", val.get("value", 0))
                if isinstance(new_affinity, str):
                    new_affinity = int(new_affinity)

        return NPCAffinityUpdateResult(
            player_id=player_id, npc_id=npc_id, new_affinity=new_affinity
        )

    async def _get_npc_context(self, npc_id: str, session_id: str) -> Dict[str, Any]:
        """NPC의 scenario와 rule 조회 (Graph fallback SQL)"""
        cypher = """
        MATCH (n:NPC {id: $npc_id, session_id: $session_id})
        RETURN {scenario: n.tid, rule: n.rule}
        LIMIT 1
        """
        results = await cypher_engine.run_cypher(
            cypher, {"npc_id": npc_id, "session_id": session_id}
        )
        if results and results[0]:
            val = results[0]
            if isinstance(val, dict):
                return {
                    "scenario": val.get("scenario", ""),
                    "rule": val.get("rule", 0),
                }
        # Fallback: SQL 조회
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_npc.sql"
        rows = await run_sql_query(sql_path, [session_id, False])
        for row in rows:
            if str(row.get("npc_id")) == npc_id:
                return {
                    "scenario": row.get("scenario_npc_id", ""),
                    "rule": row.get("rule_id", 0),
                }
        return {"scenario": "", "rule": 0}

    async def update_san(self, session_id: str, san_change: int) -> None:
        """이성(SAN) 수치 증분 업데이트"""
        sql_path = self.query_dir / "UPDATE" / "player" / "update_player_san.sql"
        await run_sql_query(sql_path, [session_id, san_change])

    # ============================================================
    # 인벤토리 헬퍼 메서드
    # ============================================================

    async def _get_player_inventory_id(self, session_id: str, player_id: str) -> str:
        """Player의 Inventory ID 조회 (Graph 우선, SQL fallback)"""
        cypher = """
        MATCH (p:Player {id: $player_id, session_id: $session_id})
              -[:HAS_INVENTORY]->(inv:Inventory)
        RETURN {inventory_id: inv.id}
        LIMIT 1
        """
        results = await cypher_engine.run_cypher(
            cypher, {"player_id": player_id, "session_id": session_id}
        )
        if results and results[0]:
            val = results[0]
            if isinstance(val, dict):
                inv_id = val.get("inventory_id")
                if inv_id:
                    return str(inv_id).strip('"')

        # Fallback: SQL 조회
        sql_path = self.query_dir / "INQUIRY" / "inventory" / "Current_inventory.sql"
        rows = await run_sql_query(sql_path, [session_id])
        if rows:
            return str(rows[0].get("inventory_id", ""))
        raise HTTPException(status_code=404, detail="Inventory not found for player")

    async def _get_item_by_rule(self, session_id: str, rule_id: int) -> Tuple[str, str]:
        """rule_id로부터 item_uuid와 scenario 조회 (Graph 우선)"""
        # Note: rule은 현재 SQL 전용이므로 Graph 노드에는 tid만 있을 수 있음.
        # 하지만 sync 시 rule 정보를 tid 등에 포함하지 않았다면 SQL 조회가 안전함.
        # 평탄화 원칙에 따라 엔티티의 정적 메타데이터(rule_id 등)는 SQL 조회가 원칙.
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_item.sql"
        rows = await run_sql_query(sql_path, [session_id])
        for row in rows:
            if row.get("rule_id") == rule_id:
                return (
                    str(row.get("item_id", "")),
                    str(row.get("scenario_item_id", "")),
                )
        raise HTTPException(
            status_code=404,
            detail=f"Item with rule_id {rule_id} not found in session",
        )

    async def _get_current_turn(self, session_id: str) -> int:
        """현재 세션의 턴 번호 조회"""
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_turn.sql"
        rows = await run_sql_query(sql_path, [session_id])
        if rows:
            return rows[0].get("current_turn", 0)
        return 0

    # ============================================================
    # 인벤토리 Cypher 기반 메서드
    # ============================================================

    async def earn_item(
        self, session_id: str, player_id: str, rule_id: int, quantity: int
    ) -> Dict[str, Any]:
        """아이템 획득 (Cypher 기반, delta 방식)

        Args:
            rule_id: 아이템 Rule ID
            quantity: 획득할 수량 (양수)
        """
        # 필요한 ID들 조회
        inventory_id = await self._get_player_inventory_id(session_id, player_id)
        item_uuid, scenario = await self._get_item_by_rule(session_id, rule_id)

        cypher_path = str(self.query_dir / "CYPHER" / "inventory" / "earn_item.cypher")
        params = {
            "player_id": player_id,
            "session_id": session_id,
            "inventory_id": inventory_id,
            "item_uuid": item_uuid,
            "scenario": scenario,
            "rule": rule_id,
            "delta_qty": quantity,
        }

        results = await cypher_engine.run_cypher(cypher_path, params)

        # 결과 처리
        new_quantity = quantity
        if results and results[0]:
            val = results[0]
            if isinstance(val, dict):
                new_quantity = val.get("quantity", val.get("value", quantity))
                if isinstance(new_quantity, str):
                    new_quantity = int(new_quantity)

        return {
            "player_id": player_id,
            "item_id": rule_id,
            "quantity": quantity,
            "total_quantity": new_quantity,
        }

    async def use_item(
        self, session_id: str, player_id: str, rule_id: int, quantity: int
    ) -> Dict[str, Any]:
        """아이템 사용 (Cypher 기반, delta 방식)

        Args:
            rule_id: 아이템 Rule ID
            quantity: 사용할 수량 (양수). 수량 부족 시 0으로 처리
        """
        # 필요한 ID들 조회
        inventory_id = await self._get_player_inventory_id(session_id, player_id)
        item_uuid, scenario = await self._get_item_by_rule(session_id, rule_id)
        current_turn = await self._get_current_turn(session_id)

        cypher_path = str(self.query_dir / "CYPHER" / "inventory" / "use_item.cypher")
        params = {
            "player_id": player_id,
            "session_id": session_id,
            "inventory_id": inventory_id,
            "item_uuid": item_uuid,
            "scenario": scenario,
            "rule": rule_id,
            "use_qty": quantity,
            "turn": current_turn,
        }

        results = await cypher_engine.run_cypher(cypher_path, params)

        # 결과 처리
        remaining_quantity = 0
        is_active = True
        if results and results[0]:
            val = results[0]
            if isinstance(val, dict):
                remaining_quantity = val.get("quantity", val.get("value", 0))
                is_active = val.get("active", True)
                if isinstance(remaining_quantity, str):
                    remaining_quantity = int(remaining_quantity)

        # turn 테이블에 아이템 사용 기록 추가
        await self._record_item_use(
            session_id, player_id, rule_id, quantity, remaining_quantity
        )

        return {
            "player_id": player_id,
            "item_id": rule_id,
            "quantity": quantity,
            "remaining_quantity": remaining_quantity,
            "active": is_active,
        }

    async def _record_item_use(
        self,
        session_id: str,
        player_id: str,
        item_id: int,
        quantity_used: int,
        remaining_quantity: int,
    ) -> None:
        """아이템 사용 기록을 turn 테이블에 추가"""
        sql_path = self.query_dir / "UPDATE" / "turn" / "record_item_use.sql"
        await run_sql_query(
            sql_path,
            [session_id, player_id, item_id, quantity_used, remaining_quantity],
        )
