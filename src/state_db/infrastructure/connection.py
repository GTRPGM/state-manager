import logging
from contextlib import asynccontextmanager
from typing import Any, Optional

import asyncpg

from state_db.configs.setting import get_db_config

logger = logging.getLogger("state_db.infrastructure.connection")


class DatabaseManager:
    """DB 연결 풀 및 리소스 관리"""

    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        if cls._pool is None:
            logger.info("Initializing database connection pool...")
            cls._pool = await asyncpg.create_pool(
                **get_db_config(),
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
    """Apache AGE 사용을 위한 search_path 설정 (public 테이블 우선)"""
    await conn.execute('SET search_path = public, ag_catalog, "$user";')
