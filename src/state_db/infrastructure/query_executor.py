import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from state_db.configs.setting import AGE_GRAPH_NAME
from state_db.infrastructure.connection import DatabaseManager, set_age_path

logger = logging.getLogger("state_db.infrastructure.query_executor")

# SQL 쿼리 캐시
SQL_CACHE: Dict[str, str] = {}


def load_queries(query_dir: Path) -> None:
    """특정 디렉토리의 SQL 파일들을 캐시에 로드"""
    global SQL_CACHE
    SQL_CACHE.clear()  # 기존 캐시 초기화 (수정 사항 반영 보장)
    count = 0
    for sql_file in query_dir.rglob("*.sql"):
        try:
            with open(sql_file, "r", encoding="utf-8") as f:
                SQL_CACHE[str(sql_file.resolve())] = f.read()
                count += 1
        except Exception as e:
            logger.error(f"Failed to load {sql_file}: {e}")
    logger.info(f"Loaded {count} SQL files into cache from {query_dir}")


async def run_sql_query(
    sql_path: Union[str, Path], params: Optional[List[Any]] = None
) -> List[Dict[str, Any]]:
    """SELECT 쿼리 실행 (파일 경로 기반)"""
    sql_path = Path(sql_path).resolve()
    sql_key = str(sql_path)

    query = SQL_CACHE.get(sql_key)
    if not query:
        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_path}")
        with open(sql_path, "r", encoding="utf-8") as f:
            query = f.read()
            SQL_CACHE[sql_key] = query

    return await run_raw_query(query, params)


async def run_raw_query(
    query: str, params: Optional[List[Any]] = None
) -> List[Dict[str, Any]]:
    """원시 SQL 쿼리 문자열 실행"""
    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)
        if params:
            rows = await conn.fetch(query, *params)
        else:
            rows = await conn.fetch(query)
    return [dict(row) for row in rows]


async def run_sql_command(
    sql_path: Union[str, Path], params: Optional[List[Any]] = None
) -> str:
    """INSERT/UPDATE/DELETE 명령 실행 (파일 경로 기반)"""
    sql_path = Path(sql_path).resolve()
    sql_key = str(sql_path)

    query = SQL_CACHE.get(sql_key)
    if not query:
        if not sql_path.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_path}")
        with open(sql_path, "r", encoding="utf-8") as f:
            query = f.read()
            SQL_CACHE[sql_key] = query

    return await run_raw_command(query, params)


async def run_raw_command(query: str, params: Optional[List[Any]] = None) -> str:
    """원시 SQL 명령 문자열 실행"""
    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)
        if params:
            result = await conn.execute(query, *params)
        else:
            result = await conn.execute(query)
    return str(result)


async def execute_sql_function(
    function_name: str, params: Optional[List[Any]] = None
) -> List[Dict[str, Any]]:
    """DB 함수 호출"""
    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)
        if params:
            placeholders = ", ".join([f"${i + 1}" for i in range(len(params))])
            query = f"SELECT {function_name}({placeholders})"
            rows = await conn.fetch(query, *params)
        else:
            query = f"SELECT {function_name}()"
            rows = await conn.fetch(query)
    return [dict(row) for row in rows]


async def run_cypher_query(
    cypher: str, params: Optional[List[Any]] = None
) -> List[Dict[str, Any]]:
    """Cypher 쿼리 실행"""
    import json

    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)
        wrapped_query = f"""
            SELECT result::text as result
            FROM ag_catalog.cypher('{AGE_GRAPH_NAME}'::name, $$
                {cypher}
            $$) AS (result agtype);
        """
        if params:
            rows = await conn.fetch(wrapped_query, *params)
        else:
            rows = await conn.fetch(wrapped_query)

    return [json.loads(row["result"]) for row in rows]
