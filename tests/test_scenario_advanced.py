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
