import json
import logging
import uuid
from typing import Any, Dict, List

from fastapi import HTTPException

from state_db.graph.cypher_engine import CypherEngine
from state_db.graph.validator import GraphValidator
from state_db.infrastructure import (
    SQL_CACHE,
    DatabaseManager,
    set_age_path,
)
from state_db.repositories.base import BaseRepository
from state_db.schemas import ScenarioInjectRequest, ScenarioInjectResponse

logger = logging.getLogger(__name__)


class ScenarioRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self.cypher = CypherEngine()

    def _get_query(self, path: Any) -> str:
        query_path = str(path.resolve())
        if query_path not in SQL_CACHE:
            with open(query_path, "r", encoding="utf-8") as f:
                SQL_CACHE[query_path] = f.read()
        return SQL_CACHE[query_path]

    async def inject_scenario(
        self, request: ScenarioInjectRequest
    ) -> ScenarioInjectResponse:
        """최종 스키마 규격에 맞춰 주입 (Act-Sequence 명칭 사용) 및 Graph 데이터 생성"""

        async with DatabaseManager.get_connection() as conn:
            await set_age_path(conn)
            async with conn.transaction():
                # 1. 시나리오 메타데이터 (SQL)
                scenario_id_row = await conn.fetchrow(
                    """
                    INSERT INTO scenario (title, description, is_published)
                    VALUES ($1, $2, true)
                    ON CONFLICT (title)
                    DO UPDATE SET description = EXCLUDED.description, updated_at = NOW()
                    RETURNING scenario_id
                    """,
                    request.title,
                    request.description,
                )
                scenario_id = str(scenario_id_row["scenario_id"])

                # 2. 클린업 (SQL & Graph)
                MASTER_SESSION_ID = "00000000-0000-0000-0000-000000000000"

                # SQL Cleanup
                cleanup_tables = ["scenario_act", "scenario_sequence"]
                for tbl in cleanup_tables:
                    await conn.execute(
                        f"DELETE FROM {tbl} WHERE scenario_id = $1",
                        scenario_id,
                    )

                cleanup_entities = ["npc", "enemy", "item"]
                for tbl in cleanup_entities:
                    await conn.execute(
                        """
                        DELETE FROM %s
                        WHERE scenario_id = $1 AND session_id = $2
                        """
                        % tbl,
                        scenario_id,
                        MASTER_SESSION_ID,
                    )

                # Graph Cleanup (Session 0 nodes for this scenario)
                await self.cypher.run_cypher(
                    """
                    MATCH (n)
                    WHERE n.scenario_id = $scenario_id
                      AND n.session_id = $session_id
                    DETACH DELETE n
                    """,
                    {"scenario_id": scenario_id, "session_id": MASTER_SESSION_ID},
                    tx=conn,
                )

                # 3. Acts (SQL)
                for act in request.acts:
                    await conn.execute(
                        """
                        INSERT INTO scenario_act (
                            scenario_id, act_id, act_name, act_description,
                            exit_criteria, sequence_ids
                        ) VALUES ($1, $2, $3, $4, $5, $6)
                        """,
                        scenario_id,
                        act.id,
                        act.name,
                        act.description,
                        act.exit_criteria,
                        act.sequences,
                    )

                # 4. Sequences & Entities (SQL + Graph)
                for seq in request.sequences:
                    await conn.execute(
                        """
                        INSERT INTO scenario_sequence (
                            scenario_id, sequence_id, sequence_name,
                            location_name, description, goal, exit_triggers
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                        """,
                        scenario_id,
                        seq.id,
                        seq.name,
                        seq.location_name,
                        seq.description,
                        seq.goal,
                        json.dumps(seq.exit_triggers),
                    )

                    # 4-1. NPCs (3-ID 체계: npc_id(UUID),
                    # scenario_npc_id(str), rule_id(int))
                    for npc_id in seq.npcs:
                        n = next(
                            (x for x in request.npcs if x.scenario_npc_id == npc_id),
                            None,
                        )
                        if n:
                            # 1. Validate first (before any DB operation)
                            node_props = {
                                "name": n.name,
                                "scenario_id": scenario_id,
                                "scenario_npc_id": n.scenario_npc_id,
                                "session_id": MASTER_SESSION_ID,
                                "active": True,
                                "rule": n.rule_id,
                                "activated_turn": 0,
                            }
                            GraphValidator.validate_node("npc", node_props)

                            # 2. Generate UUID after validation passes
                            generated_npc_id = str(uuid.uuid4())

                            # 3. SQL Insert with generated UUID
                            state = n.state or {}
                            num_state = state.get("numeric", {})
                            await conn.execute(
                                """
                                INSERT INTO npc (
                                    npc_id, name, description,
                                    scenario_id, scenario_npc_id,
                                    rule_id, session_id,
                                    assigned_sequence_id, assigned_location,
                                    tags, is_departed,
                                    hp, mp, str, dex, int, lux, san
                                ) VALUES (
                                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,
                                    $12, $13, $14, $15, $16, $17, $18
                                )
                                """,
                                generated_npc_id,
                                n.name,
                                n.description,
                                scenario_id,
                                n.scenario_npc_id,
                                n.rule_id,
                                MASTER_SESSION_ID,
                                seq.id,
                                seq.location_name,
                                n.tags,
                                n.is_departed,
                                num_state.get("HP", 100),
                                num_state.get("MP", 50),
                                num_state.get("STR"),
                                num_state.get("DEX"),
                                num_state.get("INT"),
                                num_state.get("LUX"),
                                num_state.get("SAN", 10),
                            )
                        else:
                            msg = (
                                f"NPC ID '{npc_id}' in sequence '{seq.id}' "
                                "not found in request.npcs"
                            )
                            logger.warning(msg)

                    # 4-2. Enemies (3-ID 체계: enemy_id(UUID),
                    # scenario_enemy_id(str), rule_id(int))
                    for enemy_id in seq.enemies:
                        e = next(
                            (
                                x
                                for x in request.enemies
                                if x.scenario_enemy_id == enemy_id
                            ),
                            None,
                        )
                        if e:
                            # 1. Validate first (before any DB operation)
                            node_props = {
                                "name": e.name,
                                "scenario_id": scenario_id,
                                "scenario_enemy_id": e.scenario_enemy_id,
                                "session_id": MASTER_SESSION_ID,
                                "active": True,
                                "rule": e.rule_id,
                                "activated_turn": 0,
                            }
                            GraphValidator.validate_node("enemy", node_props)

                            # 2. Generate UUID after validation passes
                            generated_enemy_id = str(uuid.uuid4())

                            # 3. SQL Insert with generated UUID
                            state = e.state or {}
                            num_state = state.get("numeric", {})
                            hp = num_state.get("HP", 30)
                            await conn.execute(
                                """
                                INSERT INTO enemy (
                                    enemy_id, name, description,
                                    scenario_id, scenario_enemy_id,
                                    rule_id, session_id,
                                    assigned_sequence_id, assigned_location,
                                    tags, dropped_items,
                                    hp, max_hp, attack, defense
                                ) VALUES (
                                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,
                                    $12, $13, $14, $15
                                )
                                """,
                                generated_enemy_id,
                                e.name,
                                e.description,
                                scenario_id,
                                e.scenario_enemy_id,
                                e.rule_id,
                                MASTER_SESSION_ID,
                                seq.id,
                                seq.location_name,
                                e.tags,
                                e.dropped_items,
                                hp,
                                hp,
                                num_state.get("attack", 10),
                                num_state.get("defense", 5),
                            )
                        else:
                            msg = (
                                f"Enemy ID '{enemy_id}' in sequence '{seq.id}' "
                                "not found in request.enemies"
                            )
                            logger.warning(msg)

                # 5. Items (SQL + Validation - 3-ID 체계:
                # item_id(UUID), scenario_item_id(str), rule_id(int))
                for item in request.items:
                    # Validate before generating UUID (same pattern as NPC/Enemy)
                    node_props = {
                        "name": item.name,
                        "scenario_id": scenario_id,
                        "scenario_item_id": item.scenario_item_id,
                        "session_id": MASTER_SESSION_ID,
                        "active": True,
                        "rule": item.rule_id,
                        "activated_turn": 0,
                    }
                    GraphValidator.validate_node("item", node_props)

                    # Generate UUID after validation passes
                    item_id = str(uuid.uuid4())

                    # SQL Insert
                    await conn.execute(
                        """
                        INSERT INTO item (
                            item_id, session_id, scenario_id,
                            scenario_item_id, rule_id, name,
                            description, item_type, meta
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        """,
                        item_id,
                        MASTER_SESSION_ID,
                        scenario_id,
                        item.scenario_item_id,
                        item.rule_id,
                        item.name,
                        item.description,
                        item.item_type,
                        json.dumps(item.meta),
                    )
                    # Note: Item Graph Nodes are typically created on demand
                    # (Inventory) or placed in world.

                # 6. Relations (Graph Edges)
                for rel in request.relations:
                    edge_props = {
                        "relation_type": rel.relation_type,
                        "affinity": rel.affinity,
                        "session_id": MASTER_SESSION_ID,
                        "scenario_id": scenario_id,
                        "active": True,
                        "activated_turn": 0,
                        "deactivated_turn": None,
                    }

                    # MERGE를 사용하여 노드 존재 보장 및 관계 생성
                    # (라벨 제거로 범용성 확보)
                    await self.cypher.run_cypher(
                        """
                        MERGE (v1 {tid: $from_id, session_id: $session_id})
                        SET v1.scenario_id = $scenario_id
                        WITH v1
                        MERGE (v2 {tid: $to_id, session_id: $session_id})
                        SET v2.scenario_id = $scenario_id
                        CREATE (v1)-[:RELATION {
                            relation_type: $relation_type,
                            affinity: $affinity,
                            session_id: $session_id,
                            scenario_id: $scenario_id,
                            active: $active,
                            activated_turn: $activated_turn
                        }]->(v2)
                        """,
                        {
                            "session_id": MASTER_SESSION_ID,
                            "scenario_id": scenario_id,
                            "from_id": rel.from_id,
                            "to_id": rel.to_id,
                            **edge_props,
                        },
                        tx=conn,
                    )

                return ScenarioInjectResponse(
                    scenario_id=scenario_id, title=request.title
                )

    async def get_all_scenarios(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM scenario ORDER BY created_at DESC"
        from state_db.infrastructure import run_raw_query

        return await run_raw_query(query)

    async def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        query = "SELECT * FROM scenario WHERE scenario_id = $1"
        from state_db.infrastructure import run_raw_query

        result = await run_raw_query(query, [scenario_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Scenario not found")

    async def get_current_context(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "INQUIRY" / "session" / "get_current_context.sql"
        from state_db.infrastructure import run_sql_query

        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Current game context not found")

    async def get_current_act_details(self, session_id: str) -> Dict[str, Any]:
        """현재 세션의 Act 상세 정보 조회"""
        sql_path = (
            self.query_dir / "INQUIRY" / "session" / "get_current_act_details.sql"
        )
        from state_db.infrastructure import run_sql_query

        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Current act details not found")

    async def get_current_sequence_details(self, session_id: str) -> Dict[str, Any]:
        """현재 세션의 Sequence 상세 정보 조회 (엔티티 및 관계 포함)"""
        from state_db.infrastructure import run_sql_query

        # 1. 시퀀스 기본 정보 조회 (SQL)
        sql_path = (
            self.query_dir / "INQUIRY" / "session" / "get_current_sequence_details.sql"
        )
        seq_result = await run_sql_query(sql_path, [session_id])
        if not seq_result:
            raise HTTPException(
                status_code=404, detail="Current sequence details not found"
            )

        sequence_info = seq_result[0]
        current_sequence_id = sequence_info["sequence_id"]

        async with DatabaseManager.get_connection() as conn:
            await set_age_path(conn)

            # 2. 현재 시퀀스의 NPC 조회 (SQL)
            npcs_rows = await conn.fetch(
                """
                SELECT npc_id, scenario_npc_id, name, description, tags,
                       hp, mp, san, str, dex, int, lux
                FROM npc
                WHERE session_id = $1 AND assigned_sequence_id = $2
                """,
                session_id,
                current_sequence_id,
            )
            npcs = [
                {
                    "id": str(row["npc_id"]),
                    "scenario_entity_id": row["scenario_npc_id"],
                    "name": row["name"],
                    "description": row["description"],
                    "entity_type": "npc",
                    "tags": row["tags"] or [],
                    "state": {
                        "numeric": {
                            "HP": row["hp"],
                            "MP": row["mp"],
                            "SAN": row["san"],
                            "STR": row["str"],
                            "DEX": row["dex"],
                            "INT": row["int"],
                            "LUX": row["lux"],
                        }
                    },
                    "is_defeated": None,
                }
                for row in npcs_rows
            ]

            # 3. 현재 시퀀스의 Enemy 조회 (SQL)
            enemies_rows = await conn.fetch(
                """
                SELECT enemy_id, scenario_enemy_id, name, description,
                       tags, is_defeated, hp, max_hp, attack, defense
                FROM enemy
                WHERE session_id = $1 AND assigned_sequence_id = $2
                """,
                session_id,
                current_sequence_id,
            )
            enemies = [
                {
                    "id": str(row["enemy_id"]),
                    "scenario_entity_id": row["scenario_enemy_id"],
                    "name": row["name"],
                    "description": row["description"],
                    "entity_type": "enemy",
                    "tags": row["tags"] or [],
                    "state": {
                        "numeric": {
                            "HP": row["hp"],
                            "max_hp": row["max_hp"],
                            "attack": row["attack"],
                            "defense": row["defense"],
                        }
                    },
                    "is_defeated": row["is_defeated"],
                }
                for row in enemies_rows
            ]

            # 4. 엔티티 간 관계 조회 (Apache AGE Graph)
            entity_relations = []
            scenario_entity_ids = [n["scenario_entity_id"] for n in npcs] + [
                e["scenario_entity_id"] for e in enemies
            ]

            if scenario_entity_ids:
                # CypherEngine을 사용하여 관계 조회
                graph_results = await self.cypher.run_cypher(
                    """
                    MATCH (v1)-[r:RELATION]->(v2)
                    WHERE r.session_id = $session_id
                    RETURN {
                        from_id: v1.tid,
                        from_name: v1.name,
                        to_id: v2.tid,
                        to_name: v2.name,
                        relation_type: r.relation_type,
                        affinity: r.affinity
                    }
                    """,
                    {"session_id": session_id},
                    tx=conn,
                )

                # 메모리 내 필터링
                for row in graph_results:
                    # ResultMapper가 맵을 Python dict로 변환함
                    from_id = row.get("from_id")
                    to_id = row.get("to_id")
                    if from_id in scenario_entity_ids or to_id in scenario_entity_ids:
                        entity_relations.append(
                            {
                                "from_id": from_id,
                                "from_name": row.get("from_name"),
                                "to_id": to_id,
                                "to_name": row.get("to_name"),
                                "relation_type": row.get("relation_type"),
                                "affinity": row.get("affinity"),
                            }
                        )

            # 5. 플레이어-NPC 관계 (Graph 기반 조회)
            player_npc_relations = []
            player_row = await conn.fetchrow(
                "SELECT player_id FROM player WHERE session_id = $1 LIMIT 1",
                session_id,
            )
            if player_row:
                player_id = str(player_row["player_id"])
                rel_rows = await self.cypher.run_cypher(
                    """
                    MATCH (p:Player {id: $player_id, session_id: $session_id})
                          -[r:RELATION]->(n:NPC)
                    WHERE r.active = true
                    RETURN {
                        npc_id: n.id,
                        npc_name: n.name,
                        scenario_npc_id: n.tid,
                        affinity_score: r.affinity,
                        relation_type: r.relation_type
                    }
                    """,
                    {"player_id": player_id, "session_id": session_id},
                )
                for row in rel_rows:
                    if row and isinstance(row, dict):
                        player_npc_relations.append(
                            {
                                "npc_id": row.get("npc_id"),
                                "npc_name": row.get("npc_name"),
                                "scenario_npc_id": row.get("scenario_npc_id"),
                                "affinity_score": row.get("affinity_score", 0),
                                "relation_type": row.get("relation_type", "neutral"),
                            }
                        )

        # 최종 결과 조합
        return {
            **sequence_info,
            "npcs": npcs,
            "enemies": enemies,
            "entity_relations": entity_relations,
            "player_npc_relations": player_npc_relations,
        }

    async def get_sequence_entity_ids(
        self, session_id: str, sequence_id: str
    ) -> Dict[str, List[str]]:
        """지정 시퀀스에 배치된 NPC/Enemy 인스턴스 ID 목록 조회."""
        async with DatabaseManager.get_connection() as conn:
            npc_rows = await conn.fetch(
                """
                SELECT npc_id
                FROM npc
                WHERE session_id = $1
                  AND assigned_sequence_id = $2
                """,
                session_id,
                sequence_id,
            )
            enemy_rows = await conn.fetch(
                """
                SELECT enemy_id
                FROM enemy
                WHERE session_id = $1
                  AND assigned_sequence_id = $2
                """,
                session_id,
                sequence_id,
            )

        return {
            "npc_ids": [str(row["npc_id"]) for row in npc_rows],
            "enemy_ids": [str(row["enemy_id"]) for row in enemy_rows],
        }

    async def advance_act(
        self, session_id: str, next_act: int, next_act_id: str, next_sequence_id: str
    ) -> Dict[str, Any]:
        """시나리오 액트 전환 (SQL 업데이트 -> 트리거를 통한 그래프 동기화)"""
        async with DatabaseManager.get_connection() as conn:
            async with conn.transaction():
                # 1. SQL 업데이트 (트리거가 그래프 Session 노드 동기화)
                await conn.execute(
                    """
                    UPDATE session
                    SET current_act = $2,
                        current_act_id = $3,
                        current_sequence = 1,
                        current_sequence_id = $4,
                        updated_at = NOW()
                    WHERE session_id = $1 AND status = 'active'
                    """,
                    session_id,
                    next_act,
                    next_act_id,
                    next_sequence_id,
                )

                # 2. 명시적 Cypher 실행 (비즈니스 로직 및 상태 확인)
                cypher_path = (
                    self.query_dir / "CYPHER" / "scenario" / "advance_act.cypher"
                )
                result = await self.cypher.run_cypher(
                    str(cypher_path),
                    {
                        "session_id": session_id,
                        "next_act_id": next_act_id,
                        "next_sequence_id": next_sequence_id,
                    },
                    tx=conn,
                )
                return result[0] if result else {}

    async def update_sequence(
        self, session_id: str, next_sequence: int, next_sequence_id: str
    ) -> Dict[str, Any]:
        """시나리오 시퀀스 전환"""
        async with DatabaseManager.get_connection() as conn:
            async with conn.transaction():
                # 1. SQL 업데이트
                await conn.execute(
                    """
                    UPDATE session
                    SET current_sequence = $2,
                        current_sequence_id = $3,
                        updated_at = NOW()
                    WHERE session_id = $1 AND status = 'active'
                    """,
                    session_id,
                    next_sequence,
                    next_sequence_id,
                )

                # 2. 명시적 Cypher 실행
                cypher_path = (
                    self.query_dir / "CYPHER" / "scenario" / "update_sequence.cypher"
                )
                result = await self.cypher.run_cypher(
                    str(cypher_path),
                    {"session_id": session_id, "next_sequence_id": next_sequence_id},
                    tx=conn,
                )
                return result[0] if result else {}
