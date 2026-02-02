"""GM 서비스 프록시"""

import logging
from typing import Any, Optional

from state_db.configs.setting import GM_URL
from state_db.proxy.client import proxy_request

logger = logging.getLogger("state_db.proxy.services.gm")


class GMProxy:
    """GM 서비스와의 통신을 담당하는 프록시 클래스"""

    base_url: str = GM_URL

    @classmethod
    async def generate_narrative(
        cls,
        session_id: str,
        context: dict[str, Any],
        prompt_type: str = "default",
        token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        내러티브 생성 요청

        Args:
            session_id: 세션 ID
            context: 컨텍스트 데이터
            prompt_type: 프롬프트 타입
            token: 인증 토큰 (선택)

        Returns:
            생성된 내러티브
        """
        logger.debug(f"Generating narrative for session {session_id}")
        return await proxy_request(
            method="POST",
            base_url=cls.base_url,
            path="/generate/narrative",
            token=token,
            json={
                "session_id": session_id,
                "context": context,
                "prompt_type": prompt_type,
            },
        )

    @classmethod
    async def generate_npc_response(
        cls,
        session_id: str,
        npc_id: str,
        player_action: str,
        context: dict[str, Any],
        token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        NPC 응답 생성 요청

        Args:
            session_id: 세션 ID
            npc_id: NPC ID
            player_action: 플레이어 액션
            context: 컨텍스트 데이터
            token: 인증 토큰 (선택)

        Returns:
            NPC 응답
        """
        logger.debug(f"Generating NPC response: {npc_id} for session {session_id}")
        return await proxy_request(
            method="POST",
            base_url=cls.base_url,
            path="/generate/npc-response",
            token=token,
            json={
                "session_id": session_id,
                "npc_id": npc_id,
                "player_action": player_action,
                "context": context,
            },
        )

    @classmethod
    async def health_check(cls) -> dict[str, Any]:
        """GM 헬스체크"""
        return await proxy_request(
            method="GET",
            base_url=cls.base_url,
            path="/health",
        )
