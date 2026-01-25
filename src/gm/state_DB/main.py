# src/gm/state_DB/main.py
# GTRPGM 상태 관리 FastAPI 서버

from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware

from .auth import create_api_key_table, get_api_key
from .configs import (
    API_ROUTERS,
    APP_ENV,
    APP_HOST,
    APP_PORT,
    CORS_ORIGINS,
    LOGGING_CONFIG,
)
from .custom import CustomJSONResponse
from .Query import shutdown as db_shutdown
from .Query import startup as db_startup

# ====================================================================
# FastAPI 앱 초기화
# ====================================================================

app = FastAPI(
    title="GTRPGM State Manager",
    description="TRPG 게임 상태를 관리하고 최신 상태를 제공하는 API",
    version="1.0.0",
    default_response_class=CustomJSONResponse,
)

# ====================================================================
# CORS 미들웨어 설정
# ====================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # 허용할 출처 목록
    allow_credentials=True,  # 쿠키 등 자격 증명 허용 여부
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

# ====================================================================
# 라우터 등록
# ====================================================================

# API 키가 필요한 엔드포인트 (State Management)
for router in API_ROUTERS:
    # auth 라우터 체크 (prefix나 tags로 구분)
    router_tags = getattr(router, "tags", [])
    if "Authentication" in router_tags or (
        hasattr(router, "prefix") and "/auth" in str(router.prefix)
    ):
        # auth 라우터는 API 키 검증 없이 등록 (API 키 생성을 위해)
        app.include_router(router, tags=["Authentication"])
    else:
        # 나머지 라우터는 API 키 검증 필요
        app.include_router(
            router,
            prefix="/state",
            tags=["State Management"],
            dependencies=[Depends(get_api_key)],
        )

# ====================================================================
# 앱 생명주기 이벤트
# ====================================================================


@app.on_event("startup")
async def on_startup():
    """서버 시작 시 DB 연결 풀 및 API 키 테이블 초기화"""
    await db_startup()
    await create_api_key_table()


@app.on_event("shutdown")
async def on_shutdown():
    """서버 종료 시 DB 연결 풀 정리"""
    await db_shutdown()


# ====================================================================
# 루트 엔드포인트
# ====================================================================


@app.get("/", description="서버 연결 확인", summary="테스트 - 서버 연결을 확인합니다.")
def read_root():
    """서버 상태 확인용 루트 엔드포인트"""
    return {
        "message": "반갑습니다. GTRPGM 상태 관리자입니다!",
        "service": "State Manager",
        "version": "1.0.0",
    }


@app.get("/health", description="헬스체크", summary="서버 헬스체크")
async def health_check():
    """헬스체크 엔드포인트 (로드밸런서/모니터링용)"""
    return {"status": "healthy"}


# ====================================================================
# 서버 실행 (개발 환경)
# ====================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=(APP_ENV == "local"),
        log_config=LOGGING_CONFIG,
    )
