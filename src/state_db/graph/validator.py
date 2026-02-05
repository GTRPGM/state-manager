from typing import Any, Dict, List, Optional

class GraphValidationError(Exception):
    """그래프 데이터 검증 실패 예외"""
    pass

class GraphValidator:
    """Graph 노드 및 엣지 데이터 정합성 검증기"""

    # 모든 노드 공통 필수 속성
    COMMON_NODE_PROPS = {"session_id", "active"}
    
    # 엔티티별 추가 필수 속성 (rule은 3-ID 체계의 핵심)
    ENTITY_NODE_PROPS = {"rule"}

    # 모든 엣지 공통 필수 속성
    COMMON_EDGE_PROPS = {"active", "activated_turn"}

    @classmethod
    def validate_node(cls, label: str, props: Dict[str, Any]) -> None:
        """
        노드 생성 전 필수 속성 검증
        :param label: 노드 라벨 (npc, enemy, item 등)
        :param props: 노드 속성 딕셔너리
        :raises GraphValidationError: 필수 속성 누락 시
        """
        missing = []
        
        # 1. 공통 속성 체크
        for p in cls.COMMON_NODE_PROPS:
            if p not in props:
                missing.append(p)

        # 2. 엔티티(npc/enemy/item)인 경우 rule 체크
        if label in ("npc", "enemy", "item"):
            for p in cls.ENTITY_NODE_PROPS:
                if p not in props:
                    missing.append(p)

        if missing:
            raise GraphValidationError(
                f"Node [{label}] missing required properties: {missing}. "
                f"Provided: {list(props.keys())}"
            )

    @classmethod
    def validate_edge(cls, rel_type: str, props: Dict[str, Any]) -> None:
        """
        엣지 생성 전 필수 속성 검증
        :param rel_type: 관계 타입 (RELATION, HAS_INVENTORY 등)
        :param props: 엣지 속성 딕셔너리
        :raises GraphValidationError: 필수 속성 누락 시
        """
        missing = []
        
        # 1. 공통 속성 체크
        for p in cls.COMMON_EDGE_PROPS:
            if p not in props:
                missing.append(p)

        if missing:
            raise GraphValidationError(
                f"Edge [{rel_type}] missing required properties: {missing}. "
                f"Provided: {list(props.keys())}"
            )
