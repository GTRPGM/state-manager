import pytest

from state_db.configs.setting import AGE_GRAPH_NAME
from state_db.infrastructure.connection import DatabaseManager


@pytest.mark.asyncio
async def test_inspect_db(db_lifecycle):
    async with DatabaseManager.get_connection() as conn:
        print(f"\n--- Testing Cypher Call with Graph Name: {AGE_GRAPH_NAME} ---")
        try:
            # We must use the correct graph name and it must exist
            res = await conn.fetch(
                f"""
                SELECT * FROM ag_catalog.cypher(
                    '{AGE_GRAPH_NAME}',
                    $$ RETURN $val as v $$,
                    $1::ag_catalog.agtype
                ) as (result ag_catalog.agtype);
            """,
                '{"val": 1}',
            )
            print(f"Success! Result: {res}")
        except Exception as e:
            print(f"Failed: {e}")
