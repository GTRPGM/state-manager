import asyncio
import os

import asyncpg

from state_db.infrastructure.connection import set_age_path


async def run():
    # Load env vars from conftest-like setup if needed,
    # but here we'll assume the user might have a local DB
    # or we use fixed ones for debugging
    # For now, let's just use what's in the env if available.
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "postgres")
    database = os.environ.get("DB_NAME", "postgres")

    conn = await asyncpg.connect(
        host=host, port=port, user=user, password=password, database=database
    )
    try:
        await set_age_path(conn)

        # Try different signatures
        graph_name = "gtrpg_graph"
        # Ensure graph exists
        await conn.execute(f"SELECT ag_catalog.create_graph('{graph_name}');")

        print("Testing signature (name, text, agtype)...")
        try:
            await conn.fetch(
                """
                SELECT * FROM ag_catalog.cypher(
                    $1::name,
                    $2::text,
                    $3::ag_catalog.agtype
                ) as (result ag_catalog.agtype);
            """,
                graph_name,
                "RETURN 1",
                "{}",
            )
            print("Success (name, text, agtype)")
        except Exception as e:
            print(f"Failed (name, text, agtype): {e}")

        print("Testing signature (name, text)...")
        try:
            await conn.fetch(
                """
                SELECT * FROM ag_catalog.cypher(
                    $1::name,
                    $2::text
                ) as (result ag_catalog.agtype);
            """,
                graph_name,
                "RETURN 1",
            )
            print("Success (name, text)")
        except Exception as e:
            print(f"Failed (name, text): {e}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run())
