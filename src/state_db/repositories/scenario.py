import json
import logging
from typing import Any, Dict, List
from uuid import UUID

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
        """캐시에서 쿼리를 가져오거나 없으면 새로 로드"""
        query_path = str(path.resolve())
        if query_path not in SQL_CACHE:
            with open(query_path, "r", encoding="utf-8") as f:
                SQL_CACHE[query_path] = f.read()
        return SQL_CACHE[query_path]

    async def inject_scenario(
        self, request: ScenarioInjectRequest
    ) -> ScenarioInjectResponse:
        """시나리오와 모든 마스터 데이터를 트랜잭션으로 주입"""

        async with DatabaseManager.get_connection() as conn:
            await set_age_path(conn)
            async with conn.transaction():
                # 1. 시나리오 삽입
                scenario_query = self._get_query(
                    self.query_dir / "MANAGE" / "scenario" / "inject_scenario.sql"
                )

                scenario_row = await conn.fetchrow(
                    scenario_query,
                    request.title,
                    request.description,
                    request.author,
                    request.version,
                    request.difficulty,
                    request.genre,
                    request.tags,
                    request.total_acts,
                )

                if not scenario_row:
                    raise HTTPException(
                        status_code=500, detail="Failed to create scenario"
                    )

                scenario_id = str(scenario_row["scenario_id"])

                # 2. NPC 삽입
                npc_query = self._get_query(
                    self.query_dir / "MANAGE" / "npc" / "inject_master_npc.sql"
                )
                npc_vertex_query = self._get_query(
                    self.query_dir / "MANAGE" / "npc" / "inject_vertex_npc.sql"
                )

                for npc in request.npcs:
                    # SQL 테이블 삽입
                    await conn.execute(
                        npc_query,
                        npc.name,
                        npc.description,
                        scenario_id,
                        npc.scenario_npc_id,
                        npc.tags,
                        json.dumps(npc.state),
                    )
                    # AGE 그래프 Vertex 생성
                    await conn.execute(
                        npc_vertex_query,
                        json.dumps(
                            {
                                "npc_id": str(
                                    UUID(int=0)
                                ),  # Master id is not used for vertex link usually
                                "session_id": "00000000-0000-0000-0000-000000000000",
                                "scenario_id": scenario_id,
                                "scenario_npc_id": npc.scenario_npc_id,
                                "name": npc.name,
                                "tags": npc.tags,
                            }
                        ),
                    )

                # 3. Enemy 삽입
                enemy_query = self._get_query(
                    self.query_dir / "MANAGE" / "enemy" / "inject_master_enemy.sql"
                )
                enemy_vertex_query = self._get_query(
                    self.query_dir / "MANAGE" / "enemy" / "inject_vertex_enemy.sql"
                )

                for enemy in request.enemies:
                    # SQL 테이블 삽입
                    await conn.execute(
                        enemy_query,
                        enemy.name,
                        enemy.description,
                        scenario_id,
                        enemy.scenario_enemy_id,
                        enemy.tags,
                        json.dumps(enemy.state),
                        enemy.dropped_items,
                    )
                    # AGE 그래프 Vertex 생성
                    await conn.execute(
                        enemy_vertex_query,
                        json.dumps(
                            {
                                "enemy_id": str(UUID(int=0)),
                                "session_id": "00000000-0000-0000-0000-000000000000",
                                "scenario_id": scenario_id,
                                "scenario_enemy_id": enemy.scenario_enemy_id,
                                "name": enemy.name,
                                "tags": enemy.tags,
                            }
                        ),
                    )

                # 4. Item 삽입
                item_query = self._get_query(
                    self.query_dir / "MANAGE" / "item" / "inject_master_item.sql"
                )

                for item in request.items:
                    await conn.execute(
                        item_query,
                        item.item_id,
                        item.name,
                        item.description,
                        scenario_id,
                        item.item_type,
                        json.dumps(item.meta),
                    )

                # 5. Relation(Edge) 삽입
                edge_query = self._get_query(
                    self.query_dir / "MANAGE" / "scenario" / "inject_edge_relation.sql"
                )
                for rel in request.relations:
                    await conn.execute(
                        edge_query,
                        json.dumps(
                            {
                                "session_id": "00000000-0000-0000-0000-000000000000",
                                "from_id": rel.from_id,
                                "to_id": rel.to_id,
                                "relation_type": rel.relation_type,
                                "affinity": rel.affinity,
                                "meta": rel.meta,
                            }
                        ),
                    )

                return ScenarioInjectResponse(
                    scenario_id=scenario_id, title=request.title
                )

    async def get_all_scenarios(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM scenario ORDER BY created_at DESC"
        # run_sql_query는 내부적으로 파일을 읽으므로 원시 쿼리는 run_raw_query 사용 권장
        from state_db.infrastructure import run_raw_query

        return await run_raw_query(query)
