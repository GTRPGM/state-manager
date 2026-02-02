"""Rule Engine 서비스 프록시"""

import logging
from typing import Any, Optional

from state_db.configs.setting import RULE_ENGINE_URL
from state_db.proxy.client import proxy_request

logger = logging.getLogger("state_db.proxy.services.rule_engine")


class RuleEngineProxy:
    """Rule Engine 서비스와의 통신을 담당하는 프록시 클래스"""

    base_url: str = RULE_ENGINE_URL

    @classmethod
    async def validate_action(
        cls,
        session_id: str,
        action_type: str,
        action_data: dict[str, Any],
        token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        액션 유효성 검증 요청

        Args:
            session_id: 세션 ID
            action_type: 액션 타입
            action_data: 액션 데이터
            token: 인증 토큰 (선택)

        Returns:
            검증 결과
        """
        logger.debug(f"Validating action: {action_type} for session {session_id}")
        return await proxy_request(
            method="POST",
            base_url=cls.base_url,
            path="/validate",
            token=token,
            json={
                "session_id": session_id,
                "action_type": action_type,
                "action_data": action_data,
            },
        )

    @classmethod
    async def calculate_outcome(
        cls,
        session_id: str,
        action_result: dict[str, Any],
        token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        액션 결과 계산 요청

        Args:
            session_id: 세션 ID
            action_result: 액션 결과 데이터
            token: 인증 토큰 (선택)

        Returns:
            계산된 결과
        """
        logger.debug(f"Calculating outcome for session {session_id}")
        return await proxy_request(
            method="POST",
            base_url=cls.base_url,
            path="/calculate",
            token=token,
            json={
                "session_id": session_id,
                "action_result": action_result,
            },
        )

    @classmethod
    async def health_check(cls) -> dict[str, Any]:
        """Rule Engine 헬스체크"""
        return await proxy_request(
            method="GET",
            base_url=cls.base_url,
            path="/health",
        )
