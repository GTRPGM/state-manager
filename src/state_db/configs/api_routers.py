# src/gm/state_db/configs/api_routers.py
# State Manager API 라우터 목록 관리

from state_db.routers import (
    router_COMMIT,
    router_INQUIRY,
    router_MANAGE,
    router_PROXY,
    router_SCENARIO,
    router_TRACE,
    router_UPDATE,
)

# State Manager의 모든 라우터 목록
API_ROUTERS = [
    router_COMMIT,  # 상태 확정 (GM용)
    router_SCENARIO,  # 시나리오 통합 관리 (목록, 주입, 검증)
    router_INQUIRY,  # 조회
    router_UPDATE,  # 업데이트
    router_MANAGE,  # 관리
    router_TRACE,  # 이력 추적 (Turn)
    router_PROXY,  # 프록시 헬스체크
]
