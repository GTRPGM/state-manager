"""Router modules for state management API.

This package contains separated routers organized by domain:
- router_SESSION: Session lifecycle and progress management
- router_INQUIRY: Data retrieval and queries
- router_UPDATE: State modifications
- router_MANAGE: Entity management
- router_TRACE: History tracking and analysis
- router_PROXY: Microservice proxy health check
"""

from . import (
    router_COMMIT,
    router_INQUIRY,
    router_MANAGE,
    router_PROXY,
    router_session,  # 파일명과 일치하게 수정
    router_TRACE,
    router_UPDATE,
)

# 별칭 제공 (기존 코드와의 호환성 및 명명 규칙 통일)
router_SESSION = router_session

__all__ = [
    "router_COMMIT",
    "router_INQUIRY",
    "router_MANAGE",
    "router_PROXY",
    "router_SESSION",
    "router_TRACE",
    "router_UPDATE",
]
