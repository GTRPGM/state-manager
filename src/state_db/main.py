# GTRPGM 상태 관리 FastAPI 서버

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, HTTPException, Request
from starlette.responses import JSONResponse

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
    """
    서버 생명주기 관리
    멱등성을 보장하며 DB 테이블을 생성하고 초기화합니다.
    """
    from state_db.infrastructure import shutdown, startup

    try:
        # 1. DB 연결 및 기초 테이블 생성 (멱등성 확보)
        # startup() 내부에서 CREATE TABLE IF NOT EXISTS 로직을 수행하도록 설계 권장
        await startup()

        # 2. 추가적인 초기화 쿼리 (필요 시)
        # 예: 기본 설정값이 없는 경우에만 삽입
        # await run_raw_query("INSERT INTO settings ... ON CONFLICT DO NOTHING")

        logger.info("🚀 Database initialization completed successfully.")
    except Exception as e:
        logger.error(f"❌ Critical Error during startup: {str(e)}")
        # 초기화 실패 시 서버 실행을 중단하는 것이 안전합니다.
        raise e

    yield

    # 서버 종료 시 연결 정리
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
# 전역 에러 로깅 미들웨어 및 예외 처리
# ====================================================================


@app.middleware("http")
async def error_logging_middleware(request: Request, call_next):
    response = await call_next(request)
    return response


init_exception_handlers(app)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
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
    from state_db.configs.api_routers import API_ROUTERS

    for router in API_ROUTERS:
        if hasattr(router, "router"):
            # 개별 라우터에서 정의한 tags를 사용하도록 수정
            app.include_router(router.router, prefix="/state")
        else:
            logger.error(f"❌ 라우터 객체를 찾을 수 없습니다: {router.__name__}")


register_routers(app)


# ====================================================================
# 루트 및 헬스체크 엔드포인트
# ====================================================================


@app.get("/", description="서버 연결 확인", summary="테스트 - 서버 연결을 확인합니다.")
def read_root() -> Dict[str, str]:
    return {
        "message": "반갑습니다. GTRPGM 상태 관리자입니다!",
        "service": "State Manager",
        "version": "1.0.0",
    }


@app.get("/health", description="서버 헬스체크", summary="헬스체크")
def health_check() -> Dict[str, str]:
    return {"status": "healthy"}


@app.get("/health/db", description="DB 연결 상태 확인", summary="DB 헬스체크")
async def db_health_check() -> Dict[str, Any]:
    from state_db.infrastructure import run_raw_query

    try:
        await run_raw_query("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"❌ DB Health Check Failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "detail": str(e),
        }


# ====================================================================
# 서버 실행
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
