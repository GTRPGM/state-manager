import logging
from pathlib import Path

from .connection import DatabaseManager, set_age_path

logger = logging.getLogger("state_db.infrastructure.schema")


async def initialize_schema(query_dir: Path) -> None:
    """DB 스키마 초기화 (테이블 및 트리거 생성)"""
    base_dir = query_dir / "BASE"

    # 의존성을 고려한 실행 순서 정의
    initial_tables = [
        "B_scenario.sql",
        "B_session.sql",
        "B_scenario_act.sql",
        "B_scenario_sequence.sql",
    ]
    entity_tables = [
        "B_player.sql",
        "B_npc.sql",
        "B_enemy.sql",
        "B_item.sql",
        "B_phase.sql",
        "B_turn.sql",
    ]
    relation_tables = [
        "B_player_inventory.sql",
        "B_player_npc_relations.sql",
        "B_inventory.sql",
    ]

    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)

        async with conn.transaction():
            # 1단계: 기본 테이블
            for filename in initial_tables:
                await _execute_sql_file(conn, base_dir / filename, "Stage 1 (Initial)")

            # 2단계: 주요 엔티티 테이블
            for filename in entity_tables:
                await _execute_sql_file(conn, base_dir / filename, "Stage 2 (Entity)")

            # 3단계: 관계 및 기타 테이블
            for filename in relation_tables:
                await _execute_sql_file(conn, base_dir / filename, "Stage 3 (Relation)")

            # 나머지 Base 파일들 (미처리된 것)
            all_processed = set(initial_tables + entity_tables + relation_tables)
            for file_path in base_dir.glob("B_*.sql"):
                if file_path.name not in all_processed:
                    await _execute_sql_file(conn, file_path, "Stage 4 (Other Base)")

            # 5단계: 로직 파일 (Triggers/Functions)
            for file_path in sorted(base_dir.glob("L_*.sql")):
                await _execute_sql_file(conn, file_path, "Stage 5 (Logic)")

    logger.info("✅ Database schema and logic initialization completed.")


async def _execute_sql_file(conn: any, file_path: Path, stage_label: str) -> None:
    """SQL 파일을 읽어 실행"""
    if file_path.exists():
        logger.debug(f"Executing {stage_label}: {file_path.name}")
        with open(file_path, "r", encoding="utf-8") as f:
            await conn.execute(f.read())
