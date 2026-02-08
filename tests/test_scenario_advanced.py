from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from state_db.repositories.scenario import ScenarioRepository
from state_db.schemas.scenario import ScenarioInjectRequest


@pytest.mark.asyncio
async def test_inject_scenario_id_reuse():
    """시나리오 주입 시 ID 재사용 및 데이터 클린업 로직 검증"""
    repo = ScenarioRepository()

    mock_request = ScenarioInjectRequest(
        scenario_id=None,
        title="Deduplication Test",
        acts=[],
        sequences=[],
        npcs=[],
        enemies=[],
        items=[],
        relations=[],
    )

    # cypher.run_cypher 모킹 (AsyncMock 필수)
    repo.cypher.run_cypher = AsyncMock(return_value=[])

    with patch(
        "state_db.repositories.scenario.DatabaseManager.get_connection"
    ) as mock_conn_ctx:
        # mock_conn을 MagicMock으로 생성 (transaction 속성 처리를 위해)
        mock_conn = MagicMock()
        mock_conn.fetchrow = AsyncMock()
        mock_conn.execute = AsyncMock()

        # transaction()이 비동기 컨텍스트 매니저를 반환하도록 설정
        mock_transaction = MagicMock()
        mock_transaction.__aenter__ = AsyncMock()
        mock_transaction.__aexit__ = AsyncMock()
        mock_conn.transaction.return_value = mock_transaction

        mock_conn_ctx.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetchrow.return_value = {
            "scenario_id": "550e8400-e29b-41d4-a716-446655440000"
        }

        result = await repo.inject_scenario(mock_request)

        assert result.scenario_id == "550e8400-e29b-41d4-a716-446655440000"
        assert mock_conn.execute.called


@pytest.mark.asyncio
async def test_get_current_context():
    """현재 세션의 맥락 정보(Act/Seq 상세) 조회 검증"""
    repo = ScenarioRepository()
    mock_session_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    mock_context = {
        "session_id": mock_session_id,
        "act_id": "act-1",
        "act_name": "The Beginning",
        "sequence_id": "seq-1",
        "sequence_name": "Tavern Talk",
        "sequence_exit_triggers": ["Talk to Kim"],
    }

    with patch(
        "state_db.infrastructure.run_sql_query",
        new=AsyncMock(return_value=[mock_context]),
    ):
        result = await repo.get_current_context(mock_session_id)

        assert result["act_id"] == "act-1"
        assert "Talk to Kim" in result["sequence_exit_triggers"]


@pytest.mark.asyncio
async def test_get_scenario_reads_item_sequence_from_meta():
    """item.assigned_sequence_id 컬럼이 없어도 meta 기반 시퀀스 매핑이 동작해야 한다."""
    repo = ScenarioRepository()
    scenario_id = "550e8400-e29b-41d4-a716-446655440000"

    async def _mock_run_raw_query(query, params=None):
        if "FROM scenario WHERE scenario_id = $1" in query:
            return [{"scenario_id": scenario_id, "title": "Meta Mapping Scenario"}]
        if "FROM scenario_act" in query:
            return []
        if "FROM scenario_sequence" in query:
            return [
                {
                    "sequence_id": "seq-1",
                    "sequence_name": "S1",
                    "location_name": "L1",
                    "description": "D1",
                    "goal": "G1",
                    "exit_triggers": [],
                    "metadata": {},
                }
            ]
        if "SELECT assigned_sequence_id, scenario_npc_id" in query:
            return []
        if "SELECT assigned_sequence_id, scenario_enemy_id" in query:
            return []
        if "FROM item" in query and "scenario_item_id" in query:
            assert "meta->>'assigned_sequence_id'" in query
            assert "assigned_sequence_ids" in query
            return [{"assigned_sequence_id": "seq-1", "scenario_item_id": "item-1"}]
        if "SELECT scenario_npc_id, name, description" in query:
            return []
        if "SELECT scenario_enemy_id, name, description" in query:
            return []
        raise AssertionError(f"Unexpected query: {query}")

    with patch("state_db.infrastructure.run_raw_query", new=AsyncMock(side_effect=_mock_run_raw_query)):
        result = await repo.get_scenario(scenario_id)

    assert result["scenario_id"] == scenario_id
    assert result["sequences"][0]["id"] == "seq-1"
    assert result["sequences"][0]["items"] == ["item-1"]


@pytest.mark.asyncio
async def test_inject_scenario_sets_item_sequence_meta():
    """시퀀스에 배치된 아이템은 item.meta에 배치 정보가 기록되어야 한다."""
    repo = ScenarioRepository()

    mock_request = ScenarioInjectRequest(
        scenario_id=None,
        title="Item Meta Mapping",
        acts=[
            {
                "id": "act-1",
                "name": "A1",
                "description": "d",
                "exit_criteria": "x",
                "sequences": ["seq-1"],
            }
        ],
        sequences=[
            {
                "id": "seq-1",
                "name": "S1",
                "location_name": "L1",
                "description": "d",
                "goal": "g",
                "exit_triggers": ["t1"],
                "metadata": {"sequence_type": "EXPLORATION"},
                "npcs": [],
                "enemies": [],
                "items": ["item-1"],
            }
        ],
        npcs=[],
        enemies=[],
        items=[
            {
                "scenario_item_id": "item-1",
                "rule_id": 7001,
                "name": "Quest Item",
                "description": "desc",
                "item_type": "quest",
                "meta": {"essential": True},
            }
        ],
        relations=[],
    )

    repo.cypher.run_cypher = AsyncMock(return_value=[])

    with patch(
        "state_db.repositories.scenario.DatabaseManager.get_connection"
    ) as mock_conn_ctx:
        mock_conn = MagicMock()
        mock_conn.fetchrow = AsyncMock(
            return_value={"scenario_id": "550e8400-e29b-41d4-a716-446655440000"}
        )
        mock_conn.execute = AsyncMock()

        mock_transaction = MagicMock()
        mock_transaction.__aenter__ = AsyncMock()
        mock_transaction.__aexit__ = AsyncMock()
        mock_conn.transaction.return_value = mock_transaction

        mock_conn_ctx.return_value.__aenter__.return_value = mock_conn

        _ = await repo.inject_scenario(mock_request)

        item_insert_calls = [
            call
            for call in mock_conn.execute.await_args_list
            if "INSERT INTO item" in call.args[0]
        ]
        seq_insert_calls = [
            call
            for call in mock_conn.execute.await_args_list
            if "INSERT INTO scenario_sequence" in call.args[0]
        ]
        assert item_insert_calls, "Expected at least one INSERT INTO item call"
        assert seq_insert_calls, "Expected at least one INSERT INTO scenario_sequence call"

        meta = item_insert_calls[0].args[9]
        assert meta["assigned_sequence_id"] == "seq-1"
        assert meta["assigned_sequence_ids"] == ["seq-1"]
        assert meta["assigned_location"] == "L1"
        assert seq_insert_calls[0].args[8] == '{"sequence_type": "EXPLORATION"}'
