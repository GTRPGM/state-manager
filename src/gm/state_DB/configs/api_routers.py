# src/gm/state_DB/configs/api_routers.py
# State Manager API 라우터 목록 관리

from ..auth_router import auth_router
from ..router import state_router

# State Manager의 모든 라우터 목록
API_ROUTERS = [
    auth_router,  # API 키 관리 (인증 불필요)
    state_router,  # 상태 관리 (API 키 필수)
]

# 향후 확장 시 추가 예시:
# from ..pipeline_router import pipeline_router
# API_ROUTERS = [
#     state_router,
#     pipeline_router,
# ]