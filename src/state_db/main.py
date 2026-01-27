# src/gm/state_db/main.py
# GTRPGM 상태 관리 FastAPI 서버

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from state_db.configs import (
    API_ROUTERS,
    APP_ENV,
    APP_PORT,
    CORS_ORIGINS,
    LOGGING_CONFIG,
)
from state_db.custom import CustomJSONResponse
from state_db.Query import shutdown as db_shutdown
from state_db.Query import startup as db_startup

# ====================================================================
# 앱 생명주기 이벤트 (Lifespan)
# ====================================================================


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """서버 생명주기 관리: 시작 시 DB 연결, 종료 시 정리"""
    # Startup logic
    await db_startup()
    # await create_main_tables()  # 테이블 이미 생성됨
    yield
    # Shutdown logic
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

# 라우터 등록
for router in API_ROUTERS:
    app.include_router(
        router,
        prefix="/state",
        tags=["State Management"],
    )

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
