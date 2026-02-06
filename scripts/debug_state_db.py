import asyncio
import os
import sys
import uuid

sys.path.append(os.getcwd())

from state_db.graph.cypher_engine import engine
from state_db.infrastructure.connection import DatabaseManager, set_age_path


async def debug_affinity():
    session_id = str(uuid.uuid4())
    player_id = str(uuid.uuid4())
    npc_id = str(uuid.uuid4())

    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)

        # 1. 노드 생성 (AGE 극소화 속성 적용)
        print("\n--- [DEBUG] 1. Creating Nodes ---")
        await engine.run_cypher(
            f"""
            CREATE (p:Player {{
                id: '{player_id}', session_id: '{session_id}',
                name: 'Hero', active: true
            }})
            CREATE (n:NPC {{
                id: '{npc_id}', session_id: '{session_id}',
                name: 'Guard', tid: 'npc-guard', active: true
            }})
            """
        )

        # 2. 첫 번째 업데이트 (+50)
        print("\n--- [DEBUG] 2. First Update (+50) ---")
        # relation.cypher 로직 수동 실행
        res1 = await engine.run_cypher(
            f"""
            MATCH (p:Player {{id: '{player_id}', session_id: '{session_id}'}})
            MATCH (n:NPC {{id: '{npc_id}', session_id: '{session_id}'}})
            MERGE (p)-[r:RELATION]->(n)
            SET r.affinity = COALESCE(r.affinity, 0) + 50
            RETURN r.affinity as affinity
            """
        )
        print(f"Result 1: {res1}")

        # 3. 두 번째 업데이트 (+20) -> 합산되는지 확인
        print("\n--- [DEBUG] 3. Second Update (+20) ---")
        res2 = await engine.run_cypher(
            f"""
            MATCH (p:Player {{id: '{player_id}', session_id: '{session_id}'}})
            MATCH (n:NPC {{id: '{npc_id}', session_id: '{session_id}'}})
            MERGE (p)-[r:RELATION]->(n)
            SET r.affinity = COALESCE(r.affinity, 0) + 20
            RETURN r.affinity as affinity
            """
        )
        print(f"Result 2: {res2}")


if __name__ == "__main__":
    asyncio.run(debug_affinity())
