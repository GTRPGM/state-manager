import uuid

import pytest

from state_db.graph.cypher_engine import engine
from state_db.infrastructure.connection import DatabaseManager
from state_db.repositories.scenario import ScenarioRepository


@pytest.mark.asyncio
async def test_advance_act_sync_graph(db_lifecycle):
    """액트 전환 시 SQL과 그래프가 동기화되는지 확인"""
    repo = ScenarioRepository()
    session_id = str(uuid.uuid4())
    scenario_id = str(uuid.uuid4())

    async with DatabaseManager.get_connection() as conn:
        await conn.execute(
            "INSERT INTO scenario (scenario_id, title) VALUES ($1, 'Test Scenario')",
            scenario_id,
        )
        # 초기 세션 생성 (트리거가 Session 노드 생성)
        await conn.execute(
            """
            INSERT INTO session (
                session_id, scenario_id, status, current_act, current_act_id
            ) VALUES ($1, $2, 'active', 1, 'act-1')
            """,
            session_id,
            scenario_id,
        )

    # 1. Advance Act 실행
    await repo.advance_act(session_id, 2, "act-2", "seq-2-1")

    # 2. SQL 상태 검증
    async with DatabaseManager.get_connection() as conn:
        row = await conn.fetchrow(
            """
            SELECT current_act, current_act_id, current_sequence_id
            FROM session WHERE session_id = $1
            """,
            session_id,
        )
        assert row["current_act"] == 2
        assert row["current_act_id"] == "act-2"
        assert row["current_sequence_id"] == "seq-2-1"

    # 3. Graph 상태 검증
    query = f"MATCH (s:Session {{id: '{session_id}'}}) RETURN s"
    results = await engine.run_cypher(query)
    assert len(results) == 1
    props = results[0]["properties"]
    assert props["current_act"] == 2
    assert props["current_act_id"] == "act-2"
    assert props["current_sequence_id"] == "seq-2-1"


@pytest.mark.asyncio
async def test_update_sequence_sync_graph(db_lifecycle):
    """시퀀스 전환 시 SQL과 그래프가 동기화되는지 확인"""
    repo = ScenarioRepository()
    session_id = str(uuid.uuid4())
    scenario_id = str(uuid.uuid4())

    async with DatabaseManager.get_connection() as conn:
        await conn.execute(
            "INSERT INTO scenario (scenario_id, title) VALUES ($1, 'Test Scenario')",
            scenario_id,
        )
        await conn.execute(
            """
            INSERT INTO session (
                session_id, scenario_id, status,
                current_sequence, current_sequence_id
            ) VALUES ($1, $2, 'active', 1, 'seq-1')
            """,
            session_id,
            scenario_id,
        )

    # 1. Update Sequence 실행
    await repo.update_sequence(session_id, 2, "seq-2")

    # 2. SQL 상태 검증
    async with DatabaseManager.get_connection() as conn:
        row = await conn.fetchrow(
            """
            SELECT current_sequence, current_sequence_id
            FROM session WHERE session_id = $1
            """,
            session_id,
        )
        assert row["current_sequence"] == 2
        assert row["current_sequence_id"] == "seq-2"

    # 3. Graph 상태 검증
    query = f"MATCH (s:Session {{id: '{session_id}'}}) RETURN s"
    results = await engine.run_cypher(query)
    assert len(results) == 1
    props = results[0]["properties"]
    assert props["current_sequence"] == 2
    assert props["current_sequence_id"] == "seq-2"
