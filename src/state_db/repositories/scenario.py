import json
import logging
from typing import Any, Dict, List

from fastapi import HTTPException

from state_db.infrastructure import (
    SQL_CACHE,
    DatabaseManager,
    set_age_path,
)
from state_db.repositories.base import BaseRepository
from state_db.schemas import ScenarioInjectRequest, ScenarioInjectResponse

logger = logging.getLogger(__name__)


class ScenarioRepository(BaseRepository):
    def _get_query(self, path: Any) -> str:
        query_path = str(path.resolve())
        if query_path not in SQL_CACHE:
            with open(query_path, "r", encoding="utf-8") as f:
                SQL_CACHE[query_path] = f.read()
        return SQL_CACHE[query_path]

    async def inject_scenario(
        self, request: ScenarioInjectRequest
    ) -> ScenarioInjectResponse:
        """최종 스키마 규격에 맞춰 주입 (Act-Sequence 명칭 사용)"""

        async with DatabaseManager.get_connection() as conn:
            await set_age_path(conn)
            async with conn.transaction():
                # 1. 시나리오
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

                # 2. 클린업
                MASTER_SESSION_ID = "00000000-0000-0000-0000-000000000000"
                await conn.execute(
                    "DELETE FROM scenario_act WHERE scenario_id = $1", scenario_id
                )
                await conn.execute(
                    "DELETE FROM scenario_sequence WHERE scenario_id = $1", scenario_id
                )
                await conn.execute(
                    "DELETE FROM npc WHERE scenario_id = $1 AND session_id = $2",
                    scenario_id,
                    MASTER_SESSION_ID,
                )
                await conn.execute(
                    "DELETE FROM enemy WHERE scenario_id = $1 AND session_id = $2",
                    scenario_id,
                    MASTER_SESSION_ID,
                )
                await conn.execute(
                    "DELETE FROM item WHERE scenario_id = $1 AND session_id = $2",
                    scenario_id,
                    MASTER_SESSION_ID,
                )
                # Graph Cleanup (Session 0 nodes for this scenario)
                await conn.execute(
                    f"""
                    SELECT * FROM ag_catalog.cypher('state_db', $$
                        MATCH (n)
                        WHERE n.scenario_id = '{scenario_id}'
                          AND n.session_id = '{MASTER_SESSION_ID}'
                        DETACH DELETE n
                    $$) AS (a agtype)
                    """
                )

                # 3. Acts
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

                # 4. Sequences & Entities (Inline Queries for precision)
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

                    for npc_id in seq.npcs:
                        n = next(
                            (x for x in request.npcs if x.scenario_npc_id == npc_id),
                            None,
                        )
                        if n:
                            await conn.execute(
                                """
                                INSERT INTO npc (
                                    name, description, scenario_id, scenario_npc_id,
                                    session_id, assigned_sequence_id, assigned_location,
                                    tags, state
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                                """,
                                n.name,
                                n.description,
                                scenario_id,
                                n.scenario_npc_id,
                                MASTER_SESSION_ID,
                                seq.id,
                                seq.location_name,
                                n.tags,
                                json.dumps(n.state),
                            )
                            # Graph Vertex (NPC)
                            await conn.execute(
                                f"""
                                SELECT * FROM ag_catalog.cypher('state_db', $$
                                    CREATE (:npc {{
                                        name: '{n.name}',
                                        scenario_id: '{scenario_id}',
                                        scenario_npc_id: '{n.scenario_npc_id}',
                                        session_id: '{MASTER_SESSION_ID}'
                                    }})
                                $$) AS (a agtype)
                                """
                            )

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
                            await conn.execute(
                                """
                                INSERT INTO enemy (
                                    name, description, scenario_id, scenario_enemy_id,
                                    session_id, assigned_sequence_id, assigned_location,
                                    tags, state, dropped_items
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                                """,
                                e.name,
                                e.description,
                                scenario_id,
                                e.scenario_enemy_id,
                                MASTER_SESSION_ID,
                                seq.id,
                                seq.location_name,
                                e.tags,
                                json.dumps(e.state),
                                e.dropped_items,
                            )
                            # Graph Vertex (Enemy)
                            await conn.execute(
                                f"""
                                SELECT * FROM ag_catalog.cypher('state_db', $$
                                    CREATE (:enemy {{
                                        name: '{e.name}',
                                        scenario_id: '{scenario_id}',
                                        scenario_enemy_id: '{e.scenario_enemy_id}',
                                        session_id: '{MASTER_SESSION_ID}'
                                    }})
                                $$) AS (a agtype)
                                """
                            )

                # 5. Items (item_id: INT, scenario_item_id: VARCHAR) #수정필요?
                for item in request.items:
                    await conn.execute(
                        """
                        INSERT INTO item (
                            item_id, session_id, scenario_id, scenario_item_id,
                            name, description, item_type, meta
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        """,
                        item.item_id,
                        MASTER_SESSION_ID,
                        scenario_id,
                        str(item.item_id),
                        item.name,
                        item.description,
                        item.item_type,
                        json.dumps(item.meta),
                    )

                # 6. Relations (Graph Edges)
                for rel in request.relations:
                    await conn.execute(
                        f"""
                        SELECT * FROM ag_catalog.cypher('state_db', $$
                            MATCH (v1), (v2)
                            WHERE v1.session_id = '{MASTER_SESSION_ID}'
                              AND (
                                v1.scenario_npc_id = '{rel.from_id}'
                                OR v1.scenario_enemy_id = '{rel.from_id}'
                              )
                              AND v2.session_id = '{MASTER_SESSION_ID}'
                              AND (
                                v2.scenario_npc_id = '{rel.to_id}'
                                OR v2.scenario_enemy_id = '{rel.to_id}'
                              )
                            CREATE (v1)-[:RELATION {{
                                relation_type: '{rel.relation_type}',
                                affinity: {rel.affinity},
                                session_id: '{MASTER_SESSION_ID}'
                            }}]->(v2)
                        $$) AS (a agtype)
                        """
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

        # 1. 시퀀스 기본 정보 조회
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

            # 2. 현재 시퀀스의 NPC 조회
            npcs_rows = await conn.fetch(
                """
                SELECT npc_id, scenario_npc_id, name, description, tags, state
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
                    "state": row["state"],
                    "is_defeated": None,
                }
                for row in npcs_rows
            ]

            # 3. 현재 시퀀스의 Enemy 조회
            enemies_rows = await conn.fetch(
                """
                SELECT enemy_id, scenario_enemy_id, name, description, tags, state, is_defeated
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
                    "state": row["state"],
                    "is_defeated": row["is_defeated"],
                }
                for row in enemies_rows
            ]

            # 4. 엔티티 간 관계 조회 (Apache AGE 그래프)
            entity_relations = []
            scenario_entity_ids = [n["scenario_entity_id"] for n in npcs] + [
                e["scenario_entity_id"] for e in enemies
            ]
            if scenario_entity_ids:
                try:
                    # 현재 세션의 엔티티들 간 관계 조회
                    relations_query = f"""
                        SELECT * FROM ag_catalog.cypher('state_db', $$
                            MATCH (v1)-[r:RELATION]->(v2)
                            WHERE r.session_id = '{session_id}'
                            RETURN
                                coalesce(v1.scenario_npc_id, v1.scenario_enemy_id) as from_id,
                                v1.name as from_name,
                                coalesce(v2.scenario_npc_id, v2.scenario_enemy_id) as to_id,
                                v2.name as to_name,
                                r.relation_type as relation_type,
                                r.affinity as affinity
                        $$) AS (from_id agtype, from_name agtype, to_id agtype, to_name agtype, relation_type agtype, affinity agtype)
                    """
                    rel_rows = await conn.fetch(relations_query)
                    for row in rel_rows:
                        from_id = str(row["from_id"]).strip('"')
                        to_id = str(row["to_id"]).strip('"')
                        # 현재 시퀀스의 엔티티들만 필터
                        if from_id in scenario_entity_ids or to_id in scenario_entity_ids:
                            entity_relations.append(
                                {
                                    "from_id": from_id,
                                    "from_name": str(row["from_name"]).strip('"'),
                                    "to_id": to_id,
                                    "to_name": str(row["to_name"]).strip('"'),
                                    "relation_type": str(row["relation_type"]).strip('"'),
                                    "affinity": int(str(row["affinity"])) if row["affinity"] else None,
                                }
                            )
                except Exception as e:
                    logger.warning(f"Failed to fetch entity relations: {e}")

            # 5. 플레이어-NPC 관계 조회
            player_npc_relations = []
            npc_ids = [n["id"] for n in npcs]
            if npc_ids:
                try:
                    pnr_rows = await conn.fetch(
                        """
                        SELECT pnr.npc_id, n.name as npc_name, n.scenario_npc_id,
                               pnr.affinity_score, pnr.relation_type, pnr.interaction_count
                        FROM player_npc_relations pnr
                        JOIN npc n ON pnr.npc_id = n.npc_id
                        JOIN player p ON pnr.player_id = p.player_id
                        WHERE p.session_id = $1 AND n.npc_id = ANY($2::uuid[])
                        """,
                        session_id,
                        npc_ids,
                    )
                    player_npc_relations = [
                        {
                            "npc_id": str(row["npc_id"]),
                            "npc_name": row["npc_name"],
                            "scenario_npc_id": row["scenario_npc_id"],
                            "affinity_score": row["affinity_score"],
                            "relation_type": row["relation_type"],
                            "interaction_count": row["interaction_count"],
                        }
                        for row in pnr_rows
                    ]
                except Exception as e:
                    logger.warning(f"Failed to fetch player-NPC relations: {e}")

        # 최종 결과 조합
        return {
            **sequence_info,
            "npcs": npcs,
            "enemies": enemies,
            "entity_relations": entity_relations,
            "player_npc_relations": player_npc_relations,
        }
