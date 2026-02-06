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


def test_validator_node_missing_entity():
    """엔티티 필수 속성(rule) 누락 시 에러 발생"""
    invalid_props = {
        "session_id": "uuid-123",
        "active": True,
        # "rule" 누락
    }
    with pytest.raises(GraphValidationError) as exc:
        GraphValidator.validate_node("npc", invalid_props)
    assert "rule" in str(exc.value)


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
    # 임시 파일 생성 없이 로직만 체크 (실제 파일 경로는 인프라 환경에 따라 다름)
    # 여기서는 초기화 상태만 확인
    assert engine.query_cache == {}
    assert engine.graph_name is not None
