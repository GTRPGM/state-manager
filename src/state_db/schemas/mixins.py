import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SessionContextMixin(BaseModel):
    """세션 식별을 위한 공통 컨텍스트"""

    session_id: str = Field(
        ...,
        description="현재 진행 중인 세션의 UUID",
        json_schema_extra={"example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
    )


class EntityBaseMixin(BaseModel):
    """엔티티(NPC, 적, 아이템 등)의 공통 기본 정보"""

    name: str = Field(
        ...,
        max_length=100,
        description="엔티티의 이름",
        json_schema_extra={"example": "Merchant Tom"},
    )
    description: Optional[str] = Field(
        "",
        description="엔티티에 대한 상세 설명",
        json_schema_extra={"example": "A friendly merchant who sells rare potions."},
    )
    tags: List[str] = Field(
        default_factory=list,
        description="엔티티 분류를 위한 태그 목록",
        json_schema_extra={"example": ["merchant", "human", "quest_giver"]},
    )


class StateMixin(BaseModel):
    """엔티티의 동적 상태 정보를 담는 공통 믹스인 (JSONB 구조 대응)"""

    state: Dict[str, Any] = Field(
        default_factory=lambda: {"numeric": {}, "boolean": {}},
        description="상태 데이터 (numeric: 수치, boolean: 플래그)",
        json_schema_extra={
            "example": {
                "numeric": {"HP": 100, "MP": 50},
                "boolean": {"is_poisoned": False},
            }
        },
    )


class LoggableMixin(BaseModel):
    """엔티티 로깅 표준화를 위한 믹스인

    로깅 시 일관된 형식으로 엔티티 정보를 출력할 수 있도록 지원합니다.
    """

    def get_log_context(self) -> Dict[str, Any]:
        """로깅에 사용할 컨텍스트 딕셔너리 반환"""
        context: Dict[str, Any] = {
            "entity_type": self.__class__.__name__,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # ID 필드 자동 감지
        for field_name in ["id", "entity_id", "session_id", "player_id", "npc_id"]:
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                if value is not None:
                    context[field_name] = str(value)
                    break

        return context

    def log_info(
        self,
        message: str,
        logger: Optional[logging.Logger] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """INFO 레벨 로깅"""
        self._log(logging.INFO, message, logger, extra)

    def log_debug(
        self,
        message: str,
        logger: Optional[logging.Logger] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """DEBUG 레벨 로깅"""
        self._log(logging.DEBUG, message, logger, extra)

    def log_warning(
        self,
        message: str,
        logger: Optional[logging.Logger] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """WARNING 레벨 로깅"""
        self._log(logging.WARNING, message, logger, extra)

    def log_error(
        self,
        message: str,
        logger: Optional[logging.Logger] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """ERROR 레벨 로깅"""
        self._log(logging.ERROR, message, logger, extra)

    def _log(
        self,
        level: int,
        message: str,
        logger: Optional[logging.Logger] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """내부 로깅 메서드"""
        if logger is None:
            logger = logging.getLogger("state_manager")

        context = self.get_log_context()
        if extra:
            context.update(extra)

        # 컨텍스트를 포함한 메시지 포맷팅
        formatted_message = f"[{context.get('entity_type', 'Unknown')}] {message}"

        # ID가 있으면 앞에 추가
        for id_field in ["id", "entity_id", "session_id"]:
            if id_field in context:
                id_value = context[id_field]
                short_id = id_value[:8] if len(id_value) > 8 else id_value
                formatted_message = f"[{short_id}...] {formatted_message}"
                break

        logger.log(level, formatted_message, extra=context)

    def to_log_string(self) -> str:
        """로깅용 문자열 표현 반환"""
        context = self.get_log_context()
        parts = [f"{k}={v}" for k, v in context.items()]
        return f"{self.__class__.__name__}({', '.join(parts)})"
