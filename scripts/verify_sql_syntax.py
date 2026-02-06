import asyncio
import logging
import os
import sys
from pathlib import Path
from uuid import uuid4

from testcontainers.postgres import PostgresContainer

# 프로젝트 루트 경로 추가 (모듈 import를 위해)
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from state_db.infrastructure import shutdown, startup  # noqa: E402
from state_db.infrastructure.connection import DatabaseManager  # noqa: E402

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("verify_sql")


async def run_verification():
    logger.info("🚀 Starting Postgres container for verification...")

    # 1. DB 컨테이너 실행
    # Using specific image as per project convention
    with PostgresContainer("ghcr.io/gtrpgm/postgres-ex:latest", port=5432) as postgres:
        # 환경 변수 주입 (DatabaseManager가 참조함)
        os.environ["DB_HOST"] = postgres.get_container_host_ip()
        os.environ["DB_PORT"] = str(postgres.get_exposed_port(5432))
        os.environ["DB_USER"] = postgres.username
        os.environ["DB_PASSWORD"] = postgres.password
        os.environ["DB_NAME"] = postgres.dbname
        os.environ["APP_ENV"] = "test"

        host = os.environ["DB_HOST"]
        port = os.environ["DB_PORT"]
        logger.info(f"✅ DB Container started at {host}:{port}")

        try:
            # 2. 애플리케이션 초기화 (initialize_schema 호출 -> SQL 파일 실행)
            logger.info("▶️  Running schema initialization (Executing all SQL files)...")
            await startup()
            logger.info(
                "✅ Schema initialization successful. (Static SQL syntax checks passed)"
            )

            # 3. 런타임 트리거 검증 (동적 SQL 체크)
            logger.info(
                "▶️  Running runtime trigger verification (Dynamic SQL check)..."
            )
            async with DatabaseManager.get_connection() as conn:
                # 3-1. Scenario 생성 (FK 제약 조건 만족용)
                scenario_id = str(uuid4())
                await conn.execute(
                    """
                    INSERT INTO scenario (scenario_id, title, description)
                    VALUES ($1, 'Verification Scenario', 'Syntax Check')
                """,
                    scenario_id,
                )
                logger.info("   - Scenario created.")

                # 3-2. Session 생성 (initialize_graph_data 트리거 동작 검증)
                session_id = str(uuid4())
                logger.info(
                    "   - Testing Session insertion (Trigger: initialize_graph_data)..."
                )
                await conn.execute(
                    """
                    INSERT INTO session (session_id, scenario_id, status)
                    VALUES ($1, $2, 'active')
                """,
                    session_id,
                    scenario_id,
                )
                logger.info("     -> Success.")

                # 3-3. Player 생성 (sync_entity_to_graph 트리거 동작 검증)
                logger.info(
                    "   - Testing Player insertion (Trigger: sync_entity_to_graph)..."
                )
                await conn.execute(
                    """
                    INSERT INTO player (player_id, session_id, name, hp, mp, san)
                    VALUES ($1, $2, 'Test Player', 100, 50, 10)
                """,
                    str(uuid4()),
                    session_id,
                )
                logger.info("     -> Success.")

                # 3-4. Update 테스트 (sync_entity_to_graph 트리거 Update 동작 검증)
                logger.info(
                    "   - Testing Player update (Trigger: sync_entity_to_graph)..."
                )
                await conn.execute(
                    """
                    UPDATE player SET name = 'Updated Player' WHERE session_id = $1
                """,
                    session_id,
                )
                logger.info("     -> Success.")

            # 4. Pure Cypher 파일 검증
            logger.info("▶️  Running pure Cypher files verification...")
            from state_db.graph.cypher_engine import engine

            cypher_dir = project_root / "src" / "state_db" / "Query" / "CYPHER"
            cypher_files = list(cypher_dir.rglob("*.cypher"))
            logger.info(f"   - Found {len(cypher_files)} .cypher files.")

            dummy_params = {
                "session_id": session_id,
                "player_id": str(uuid4()),
                "inventory_id": str(uuid4()),
                "item_uuid": str(uuid4()),
                "npc_uuid": str(uuid4()),
                "scenario": "test",
                "rule": 1,
                "delta_qty": 1,
                "use_qty": 1,
                "delta_affinity": 10,
                "relation_type": "neutral",
                "turn": 1,
                "meta_json": "{}",
                "include_inactive": False,
                "next_act_id": "act-next",
                "next_sequence_id": "seq-next",
            }

            for cf in cypher_files:
                rel_path = cf.relative_to(cypher_dir)
                try:
                    # 실제 실행 대신 EXPLAIN으로 문법 체크를 하고 싶지만
                    # AGE는 EXPLAIN 지원이 제한적일 수 있음.
                    # 따라서 실제 실행하되 트랜잭션 롤백을 활용하거나,
                    # 읽기 전용으로 체크.
                    # 여기서는 간단히 실행해보고 에러가 나는지만 확인
                    # (데이터가 없으므로 빈 결과가 나오거나 에러)
                    # 단, 파라미터가 없으면 에러가 날 수 있으므로
                    # 더미 파라미터 주입

                    # 파일 경로를 엔진이 인식하는 상대 경로 키로 변환
                    # (예: inventory/earn_item.cypher)
                    # 엔진은 registry를 통해 로드하므로 절대 경로를
                    # 직접 사용하지 않고 load_query를 이용하거나
                    # 직접 텍스트를 읽어서 run_cypher에 주입해야 함.
                    # 여기서는 엔진의 정규화 로직까지 테스트하기 위해
                    # run_cypher 사용

                    # 쿼리 캐시에 강제 로드 (경로 문제 회피)
                    engine.load_query(cf)

                    # 실행 (경로 기반)
                    # 주의: registry는 "inventory/earn_item.cypher" 형태의
                    # 키를 기대할 수 있음. 하지만 load_query는 절대경로로
                    # 로드하고 cache에는 절대경로로 저장됨.
                    # run_cypher는 절대경로 키를 받아서 실행 가능.

                    await engine.run_cypher(str(cf), dummy_params)
                    logger.info(f"   - ✅ {rel_path} passed.")
                except Exception as e:
                    logger.error(f"   - ❌ {rel_path} FAILED: {e}")
                    raise

            logger.info("🎉 All SQL, Trigger, and Cypher verifications PASSED!")

        except Exception as e:
            logger.error(f"❌ Verification FAILED: {e}")
            # 에러 발생 시 상세 정보가 로그에 남음
            sys.exit(1)
        finally:
            logger.info("🛑 Shutting down application...")
            await shutdown()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_verification())
