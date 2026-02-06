import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from state_db.infrastructure import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cleanup_legacy")


async def main():
    tables_to_drop = [
        "player_inventory",
        "inventory_item",
        "player_npc_relations",
        "npc_relations",  # Just in case
    ]

    async with DatabaseManager.get_connection() as conn:
        for table in tables_to_drop:
            try:
                logger.info(f"Dropping table {table} if exists...")
                await conn.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                logger.info(f"Dropped {table}.")
            except Exception as e:
                logger.error(f"Error dropping {table}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
