import uuid

import pytest

from state_db.graph.cypher_engine import engine
from state_db.infrastructure.connection import DatabaseManager


@pytest.mark.asyncio
async def test_sync_player_trigger(db_lifecycle):
    """
    Verify that inserting a Player row triggers Graph Node creation.
    """
    session_id = str(uuid.uuid4())
    scenario_id = str(uuid.uuid4())
    player_id = str(uuid.uuid4())

    async with DatabaseManager.get_connection() as conn:
        # 0. Create Scenario (Required for session FK)
        await conn.execute(
            """
            INSERT INTO scenario (scenario_id, title, description)
            VALUES ($1, 'Test Scenario', 'Description')
        """,
            scenario_id,
        )

        # 1. Create Session (Required FK)
        await conn.execute(
            """
            INSERT INTO session (session_id, scenario_id, status)
            VALUES ($1, $2, 'active')
        """,
            session_id,
            scenario_id,
        )

        # 2. Insert Player
        await conn.execute(
            """
            INSERT INTO player (player_id, session_id, name, state)
            VALUES ($1, $2, 'Test Sync Player', '{"numeric": {"HP": 100}}')
        """,
            player_id,
            session_id,
        )

    # 3. Verify Graph Node
    # Note: L_graph.sql trigger creates node with label :Player
    query = f"""
    MATCH (n:Player)
    WHERE n.player_id = '{player_id}' AND n.session_id = '{session_id}'
    RETURN n
    """

    results = await engine.run_cypher(query)

    assert len(results) == 1
    # ResultMapper returns the vertex object directly in list
    node_props = results[0]["properties"]

    # Check properties
    # Note: row_to_json produces lowercase keys.
    assert node_props["player_id"] == player_id
    assert node_props["name"] == "Test Sync Player"
    # Check JSONB mapping
    # agtype parses nested json.
    # Note: AGE might store json as string or dict depending on driver.
    # Based on mapper, it seems it parses json.
    assert node_props["state"]["numeric"]["HP"] == 100


@pytest.mark.asyncio
async def test_sync_npc_trigger_update(db_lifecycle):
    """
    Verify NPC insert and update sync from SQL to Graph.
    """
    session_id = str(uuid.uuid4())
    scenario_id = str(uuid.uuid4())
    npc_id = str(uuid.uuid4())

    async with DatabaseManager.get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO scenario (scenario_id, title, description)
            VALUES ($1, 'Test Scenario', 'Description')
        """,
            scenario_id,
        )

        await conn.execute(
            """
            INSERT INTO session (session_id, scenario_id, status)
            VALUES ($1, $2, 'active')
        """,
            session_id,
            scenario_id,
        )

        # Insert NPC
        await conn.execute(
            """
            INSERT INTO npc (
                npc_id, session_id, scenario_id, scenario_npc_id, name, rule_id
            )
            VALUES ($1, $2, $3, 'npc_01', 'Old NPC', 101)
        """,
            npc_id,
            session_id,
            scenario_id,
        )

    # Verify Create
    query_chk = f"""
    MATCH (n:NPC) WHERE n.npc_id = '{npc_id}' RETURN n
    """
    res1 = await engine.run_cypher(query_chk)
    assert len(res1) == 1
    assert res1[0]["properties"]["name"] == "Old NPC"

    # Update NPC
    async with DatabaseManager.get_connection() as conn:
        await conn.execute(
            """
            UPDATE npc SET name = 'Updated NPC', is_departed = true
            WHERE npc_id = $1
        """,
            npc_id,
        )

    # Verify Update
    res2 = await engine.run_cypher(query_chk)
    assert len(res2) == 1
    node_props = res2[0]["properties"]
    assert node_props["name"] == "Updated NPC"
    # AGE boolean is boolean
    assert node_props["is_departed"] is True


@pytest.mark.asyncio
async def test_session_init_copy(db_lifecycle):
    """
    Verify initialize_graph_data copies template data from Master Session
    to the new session.
    """
    master_session_id = "00000000-0000-0000-0000-000000000000"
    scenario_id = str(uuid.uuid4())
    new_session_id = str(uuid.uuid4())

    # 1. Setup Master Data in Graph
    # Inject Template Nodes manually
    await engine.run_cypher(f"""
        CREATE (:NPC {{
            session_id: '{master_session_id}',
            scenario_id: '{scenario_id}',
            scenario_npc_id: 'template_npc',
            name: 'Template NPC'
        }})
    """)

    await engine.run_cypher(f"""
        CREATE (:Item {{
            session_id: '{master_session_id}',
            scenario_id: '{scenario_id}',
            scenario_item_id: 'template_item',
            name: 'Template Item'
        }})
    """)

    # 2. Insert New Session
    async with DatabaseManager.get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO scenario (scenario_id, title, description)
            VALUES ($1, 'Test Scenario', 'Description')
        """,
            scenario_id,
        )

        await conn.execute(
            """
            INSERT INTO session (session_id, scenario_id, status)
            VALUES ($1, $2, 'active')
        """,
            new_session_id,
            scenario_id,
        )

    # 3. Verify Copy
    # Should have copied NPC and Item with new session_id
    res_npc = await engine.run_cypher(f"""
        MATCH (n:NPC) WHERE n.session_id = '{new_session_id}' RETURN n
    """)
    assert len(res_npc) == 1
    assert res_npc[0]["properties"]["name"] == "Template NPC"

    res_item = await engine.run_cypher(f"""
        MATCH (n:Item) WHERE n.session_id = '{new_session_id}' RETURN n
    """)
    assert len(res_item) == 1
    assert res_item[0]["properties"]["name"] == "Template Item"
