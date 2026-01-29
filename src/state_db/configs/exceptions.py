import logging

import asyncpg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("uvicorn.error")


def init_exception_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"🔥 Unhandled Exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "서버 내부 오류가 발생했습니다.",
                "detail": str(exc),
            },
        )

    @app.exception_handler(asyncpg.PostgresError)
    async def db_exception_handler(request: Request, exc: asyncpg.PostgresError):
        logger.error(f"🗄️ Database Error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "데이터베이스 처리 중 오류가 발생했습니다.",
                "detail": str(exc),
            },
        )
