import pytest

from state_db.graph.cypher_engine import CypherEngine
from state_db.graph.validator import GraphValidationError, GraphValidator


def test_validator_node_success():
    """노드 검증 성공 케이스"""
    valid_props = {
        "session_id": "uuid-123",
        "active": True,
        "rule": 10,
        "name": "Test NPC",
    }
    # 에러가 발생하지 않아야 함
    GraphValidator.validate_node("npc", valid_props)


def test_validator_node_missing_common():
    """공통 필수 속성 누락 시 에러 발생"""
    invalid_props = {
        "session_id": "uuid-123"
        # "active" 누락
    }
    with pytest.raises(GraphValidationError) as exc:
        GraphValidator.validate_node("npc", invalid_props)
    assert "active" in str(exc.value)


def test_validator_edge_success():
    """엣지 검증 성공 케이스"""
    valid_props = {"active": True, "activated_turn": 0}
    GraphValidator.validate_edge("RELATION", valid_props)


def test_validator_edge_missing():
    """엣지 필수 속성 누락 시 에러 발생"""
    invalid_props = {
        "active": True
        # "activated_turn" 누락
    }
    with pytest.raises(GraphValidationError) as exc:
        GraphValidator.validate_edge("RELATION", invalid_props)
    assert "activated_turn" in str(exc.value)

    @pytest.mark.asyncio
    async def test_cypher_engine_loading():
        """Cypher 엔진의 쿼리 로딩 및 캐싱 테스트"""
        engine = CypherEngine()
        # 다른 테스트에 의해 이미 로드되었을 수 있으므로 캐시를 비우고 테스트
        engine.query_cache.clear()
        assert engine.query_cache == {}
        assert engine.graph_name is not None
