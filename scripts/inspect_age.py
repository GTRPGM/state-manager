import asyncio
import os

import asyncpg


async def run():
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "postgres")
    database = os.environ.get("DB_NAME", "postgres")

    conn = await asyncpg.connect(
        host=host, port=port, user=user, password=password, database=database
    )
    try:
        # Check cypher functions
        rows = await conn.fetch("""
            SELECT n.nspname as schema, p.proname as name,
                   pg_get_function_arguments(p.oid) as args
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE p.proname = 'cypher';
        """)
        for row in rows:
            print(f"Function: {row['schema']}.{row['name']}({row['args']})")

        # Check agtype
        rows = await conn.fetch("""
            SELECT n.nspname as schema, t.typname as name
            FROM pg_type t
            JOIN pg_namespace n ON t.typnamespace = n.oid
            WHERE t.typname = 'agtype';
        """)
        for row in rows:
            print(f"Type: {row['schema']}.{row['name']}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run())
