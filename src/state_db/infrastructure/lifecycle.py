import logging
from pathlib import Path

from state_db.configs.setting import AGE_GRAPH_NAME
from state_db.infrastructure.connection import DatabaseManager, set_age_path
from state_db.infrastructure.query_executor import load_queries

logger = logging.getLogger("state_db.infrastructure.lifecycle")


async def init_age_graph() -> None:
    """Apache AGE 그래프 초기화"""
    async with DatabaseManager.get_connection() as conn:
        # 0. extension 로드 및 기초 설정
        await conn.execute("CREATE EXTENSION IF NOT EXISTS age CASCADE;")
        await conn.execute("LOAD 'age';")

        await set_age_path(conn)
        graph_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM ag_catalog.ag_graph WHERE name = $1)",
            AGE_GRAPH_NAME,
        )
        if not graph_exists:
            await conn.execute("SELECT create_graph($1);", AGE_GRAPH_NAME)
            logger.info(f"Graph '{AGE_GRAPH_NAME}' created")
        else:
            logger.debug(f"Graph '{AGE_GRAPH_NAME}' already exists")


async def startup() -> None:
    """애플리케이션 시작 시 초기화"""
    from .schema import initialize_schema

    await DatabaseManager.get_pool()

    # 쿼리 로드 (상위 폴더의 Query 디렉토리)
    # 현재 파일 위치: src/state_db/infrastructure/lifecycle.py
    # 목표: src/state_db/Query
    query_dir = Path(__file__).parent.parent / "Query"
    load_queries(query_dir)

    # 1. AGE 초기화
    await init_age_graph()

    # 2. 스키마 초기화 (테이블 및 트리거 생성)
    await initialize_schema(query_dir)


async def shutdown() -> None:
    """애플리케이션 종료 시 정리"""
    await DatabaseManager.close_pool()
