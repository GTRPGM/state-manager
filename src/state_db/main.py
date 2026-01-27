# GTRPGM 상태 관리 FastAPI 서버

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, HTTPException, Request
from starlette.responses import JSONResponse

# [수정] 최상단에서 Query와 API_ROUTERS 임포트를 제거했습니다.
from state_db.configs import (
    APP_ENV,
    APP_PORT,
    LOGGING_CONFIG,
)
from state_db.configs.exceptions import init_exception_handlers
from state_db.custom import CustomJSONResponse

logger = logging.getLogger("uvicorn.error")


# ====================================================================
# 앱 생명주기 이벤트 (Lifespan)
# ====================================================================


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """서버 생명주기 관리"""
    import asyncio

    from state_db.infrastructure import shutdown, startup

    # DB 연결 및 초기화를 백그라운드 태스크로 실행
    asyncio.create_task(startup())
    yield
    await shutdown()


# ====================================================================
# FastAPI 앱 초기화
# ====================================================================

app = FastAPI(
    title="GTRPGM State Manager",
    description="TRPG 게임 상태를 관리하고 최신 상태를 제공하는 API",
    version="1.0.0",
    default_response_class=CustomJSONResponse,
    lifespan=lifespan,
)


# ====================================================================
# 전역 에러 로깅 미들웨어
# ====================================================================


@app.middleware("http")
async def error_logging_middleware(request: Request, call_next):
    # 이제 에러 로그는 핸들러가 담당하므로 미들웨어는 통과만 시킵니다.
    response = await call_next(request)
    return response


init_exception_handlers(app)


# ====================================================================
# HTTPException 전용 핸들러
# ====================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # 여기서 로그를 남겨야 터미널에 에러가 찍힙니다.
    logger.error(
        f"❌ HTTP {exc.status_code} Error: {request.method} {request.url.path}"
    )
    logger.error(f"Detail: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": "요청 처리 중 오류가 발생했습니다.",
            "detail": exc.detail,
        },
    )


# ====================================================================
# 라우터 등록
# ====================================================================


def register_routers(app: FastAPI):
    # [수정] 이 시점에 로드하면 Query 모듈이 이미 준비되어
    # 순환 참조가 발생하지 않습니다.
    from state_db.configs.api_routers import API_ROUTERS

    for router in API_ROUTERS:
        app.include_router(
            router,
            prefix="/state",
            tags=["State Management"],
        )


register_routers(app)

# ====================================================================
# 루트 엔드포인트
# ====================================================================


@app.get("/", description="서버 연결 확인", summary="테스트 - 서버 연결을 확인합니다.")
def read_root() -> Dict[str, str]:
    """서버 상태 확인용 루트 엔드포인트"""
    return {
        "message": "반갑습니다. GTRPGM 상태 관리자입니다!",
        "service": "State Manager",
        "version": "1.0.0",
    }


@app.get("/health", description="헬스체크", summary="서버 헬스체크")
async def health_check() -> Dict[str, str]:
    """헬스체크 엔드포인트 (로드밸런서/모니터링용)"""
    return {"status": "healthy"}


@app.get("/health/db", description="DB 연결 상태 확인", summary="DB 헬스체크")
async def db_health_check() -> Dict[str, Any]:
    """데이터베이스 연결 상태를 실시간으로 확인합니다."""
    from state_db.infrastructure import run_sql_query

    try:
        # 매우 가벼운 쿼리로 연결 확인
        await run_sql_query("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "message": "DB 연결이 정상입니다.",
        }
    except Exception as e:
        logger.error(f"❌ DB Health Check Failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "detail": str(e),
        }


# ====================================================================
# 서버 실행 (개발 환경)
# ====================================================================

if __name__ == "__main__":
    import uvicorn

    effective_host = "127.0.0.1" if APP_ENV == "local" else "0.0.0.0"

    uvicorn.run(
        "main:app",
        host=effective_host,
        port=APP_PORT,
        reload=(APP_ENV == "local"),
        log_config=LOGGING_CONFIG,
    )
