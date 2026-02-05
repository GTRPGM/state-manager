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
                    INSERT INTO player (player_id, session_id, name, state)
                    VALUES ($1, $2, 'Test Player', '{"numeric": {"HP": 100}}')
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

            logger.info("🎉 All SQL and Trigger verifications PASSED!")

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
