# src/gm/state_db/main.py
# GTRPGM 상태 관리 FastAPI 서버

import logging
import traceback
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

# [수정] 최상단에서 Query와 API_ROUTERS 임포트를 제거했습니다.
from state_db.configs import (
    APP_ENV,
    APP_PORT,
    CORS_ORIGINS,
    LOGGING_CONFIG,
)
from state_db.custom import CustomJSONResponse

logger = logging.getLogger("uvicorn.error")


# ====================================================================
# 앱 생명주기 이벤트 (Lifespan)
# ====================================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """서버 생명주기 관리: 함수 내부에서 임포트하여 순환 참조 방지"""
    # [수정] 실행 시점에 필요한 함수만 임포트
    from state_db.Query import startup as db_startup
    from state_db.Query import shutdown as db_shutdown

    await db_startup()
    yield
    await db_shutdown()


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


# 1. 일반적인 모든 서버 에러 (500)
@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    logger.error(f"🔥 Unexpected Error: {request.method} {request.url.path}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "서버 내부 오류가 발생했습니다.",
            "detail": str(exc),
        },
    )


# 2. 의도된 HTTP 에러 (400, 401, 404, 503 등) - 중복 제거 및 통합
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"⚠️ HTTP {exc.status_code} Error: {request.method} {request.url.path}")
    logger.error(f"Detail: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": "요청 처리 중 오류가 발생했습니다.",
            "detail": exc.detail,
        },
    )


# 3. 데이터 검증 에러 (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_details = []
    for error in errors:
        loc = " -> ".join([str(x) for x in error.get("loc", [])])
        msg = error.get("msg")
        inp = error.get("input")
        error_details.append(f"[{loc}] {msg} (Input: {inp})")

    full_message = " | ".join(error_details)
    logger.error(f"❌ Validation Error: {request.method} {request.url.path}")
    logger.error(f"Detail: {full_message}")

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "message": "입력값 검증에 실패했습니다.",
            "detail": errors,
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================================================================
# HTTPException 전용 핸들러
# ====================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # 여기서 로그를 남겨야 터미널에 에러가 찍힙니다.
    logger.error(f"❌ HTTP {exc.status_code} Error: {request.method} {request.url.path}")
    logger.error(f"Detail: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": "요청 처리 중 오류가 발생했습니다.",
            "detail": exc.detail
        }
    )

# ====================================================================
# 라우터 등록
# ====================================================================

def register_routers(app: FastAPI):
    # [수정] 이 시점에 로드하면 Query 모듈이 이미 준비되어 순환 참조가 발생하지 않습니다.
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
