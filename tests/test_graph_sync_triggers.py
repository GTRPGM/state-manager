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
            INSERT INTO player (player_id, session_id, name, hp, mp, san)
            VALUES ($1, $2, 'Test Sync Player', 100, 50, 10)
        """,
            player_id,
            session_id,
        )

    # 3. Verify Graph Node
    # Note: L_graph.sql trigger creates node with label :Player
    query = f"""
    MATCH (n:Player)
    WHERE n.id = '{player_id}' AND n.session_id = '{session_id}'
    RETURN n
    """

    results = await engine.run_cypher(query)

    assert len(results) == 1
    # ResultMapper returns the vertex object directly in list
    node_props = results[0]["properties"]

    # Check properties
    assert node_props["id"] == player_id
    assert node_props["name"] == "Test Sync Player"
    # state is no longer synced to Graph Node per minimalist approach
    assert "state" not in node_props


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
    MATCH (n:NPC) WHERE n.id = '{npc_id}' RETURN n
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
    # active is the promoted flag in Graph Node
    assert node_props["active"] is False


@pytest.mark.asyncio
async def test_session_init_copy(db_lifecycle):
    """
    Verify initialize_graph_data copies relationships from Master Session.
    Nodes are expected to be synced via SQL cloning + table triggers.
    """
    master_session_id = "00000000-0000-0000-0000-000000000000"
    scenario_id = str(uuid.uuid4())
    new_session_id = str(uuid.uuid4())
    npc1_id = str(uuid.uuid4())
    npc2_id = str(uuid.uuid4())

    async with DatabaseManager.get_connection() as conn:
        # 0. Setup Scenario
        await conn.execute(
            "INSERT INTO scenario (scenario_id, title) VALUES ($1, 'Rel Test')",
            scenario_id,
        )

        # 1. Setup Master Data in SQL (Triggers will create Graph Nodes with 'tid')
        await conn.execute(
            """
            INSERT INTO npc (npc_id, session_id, scenario_id, scenario_npc_id, name)
            VALUES ($1, $2, $3, 'n1', 'NPC 1'), ($4, $2, $3, 'n2', 'NPC 2')
            """,
            npc1_id,
            master_session_id,
            scenario_id,
            npc2_id,
        )

    # 2. Setup Master Relationship in Graph
    await engine.run_cypher(
        f"""
        MATCH (n1:NPC {{id: '{npc1_id}', session_id: '{master_session_id}'}})
        MATCH (n2:NPC {{id: '{npc2_id}', session_id: '{master_session_id}'}})
        CREATE (n1)-[:RELATION {{
            relation_type: 'friend', affinity: 80,
            session_id: '{master_session_id}', scenario_id: '{scenario_id}'
        }}]->(n2)
    """
    )

    # 3. Insert New Session (Triggers SQL cloning -> Node Sync -> Relation Copy)
    async with DatabaseManager.get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO session (session_id, scenario_id, status)
            VALUES ($1, $2, 'active')
        """,
            new_session_id,
            scenario_id,
        )

    # 4. Verify Nodes and Relationship in New Session
    # Nodes should exist due to L_npc.sql cloning + trg_sync_npc_graph
    res_nodes = await engine.run_cypher(
        f"MATCH (n:NPC) WHERE n.session_id = '{new_session_id}' RETURN n"
    )
    assert len(res_nodes) == 2

    # Relationship should be copied via initialize_graph_data (matching by tid)
    res_rel = await engine.run_cypher(
        f"""
        MATCH (n1:NPC {{tid: 'n1', session_id: '{new_session_id}'}})
              -[r:RELATION]->
              (n2:NPC {{tid: 'n2', session_id: '{new_session_id}'}})
        RETURN r
    """
    )
    assert len(res_rel) == 1
    assert res_rel[0]["properties"]["affinity"] == 80
