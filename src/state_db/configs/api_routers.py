# src/gm/state_db/configs/api_routers.py
# State Manager API 라우터 목록 관리

from state_db.routers import (
    router_INJECT,
    router_INQUIRY,
    router_MANAGE,
    router_START,
    router_TRACE,
    router_TRACE_phase,
    router_UPDATE,
)

# State Manager의 모든 라우터 목록
API_ROUTERS = [
    router_INJECT,  # 시나리오 주입
    router_START,  # 세션 시작
    router_INQUIRY,  # 조회
    router_UPDATE,  # 업데이트
    router_MANAGE,  # 관리
    router_TRACE,  # 이력 추적 (Turn)
    router_TRACE_phase,  # 이력 추적 (Phase)
]
