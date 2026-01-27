import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import asyncpg

from state_db.configs.setting import AGE_GRAPH_NAME, DB_CONFIG

logger = logging.getLogger("state_db.infrastructure.database")

# SQL 쿼리 캐시
SQL_CACHE: Dict[str, str] = {}


class DatabaseManager:
    """DB 연결 풀 및 리소스 관리"""

    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        if cls._pool is None:
            logger.info("Initializing database connection pool...")
            cls._pool = await asyncpg.create_pool(
                **DB_CONFIG,
                min_size=2,
                max_size=10,
                command_timeout=60,
            )
        return cls._pool

    @classmethod
    async def close_pool(cls) -> None:
        if cls._pool:
            logger.info("Closing database connection pool...")
            await cls._pool.close()
            cls._pool = None

    @classmethod
    @asynccontextmanager
    async def get_connection(cls) -> Any:
        pool = await cls.get_pool()
        async with pool.acquire() as connection:
            yield connection


async def set_age_path(conn: asyncpg.Connection) -> None:
    """Apache AGE 사용을 위한 search_path 설정"""
    await conn.execute('SET search_path = ag_catalog, "$user", public;')


async def init_age_graph() -> None:
    """Apache AGE 그래프 초기화"""
    async with DatabaseManager.get_connection() as conn:
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


def load_queries(query_dir: Path) -> None:
    """특정 디렉토리의 SQL 파일들을 캐시에 로드"""
    global SQL_CACHE
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
    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)
        wrapped_query = f"""
            SELECT result::jsonb
            FROM cypher('{AGE_GRAPH_NAME}', $$
                {cypher}
            $$) AS (result agtype);
        """
        if params:
            rows = await conn.fetch(wrapped_query, *params)
        else:
            rows = await conn.fetch(wrapped_query)
    return [row["result"] for row in rows]


async def startup() -> None:
    """애플리케이션 시작 시 초기화"""
    await DatabaseManager.get_pool()

    # 쿼리 로드 (상위 폴더의 Query 디렉토리)
    query_dir = Path(__file__).parent.parent / "Query"
    load_queries(query_dir)

    # AGE 초기화
    await init_age_graph()


async def shutdown() -> None:
    """애플리케이션 종료 시 정리"""
    await DatabaseManager.close_pool()
