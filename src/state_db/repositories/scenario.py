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

                # 5. Items
                for item in request.items:
                    await conn.execute(
                        """
                        INSERT INTO item (
                            session_id, scenario_id, scenario_item_id,
                            name, description, item_type, meta
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                        """,
                        MASTER_SESSION_ID,
                        scenario_id,
                        item.item_id,
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
