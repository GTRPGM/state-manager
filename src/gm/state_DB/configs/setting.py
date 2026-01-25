# src/gm/state_DB/configs/setting.py
# State Manager 설정값 관리

import os

# ====================================================================
# PostgreSQL 데이터베이스 설정
# ====================================================================
DB_USER = os.getenv("DB_USER", "state_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "state_password")
DB_NAME = os.getenv("DB_NAME", "state_db")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

# Apache AGE 그래프 설정
AGE_GRAPH_NAME = os.getenv("AGE_GRAPH_NAME", "state_db")

# ====================================================================
# 서버 설정
# ====================================================================
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")  # local: 127.0.0.1, prod: 0.0.0.0
APP_PORT = int(os.getenv("APP_PORT", "8000"))  # State Manager 포트
APP_ENV = os.getenv("APP_ENV", "local")  # local, dev, prod

# ====================================================================
# 원격 호스트 설정
# ====================================================================
REMOTE_HOST = os.getenv("REMOTE_HOST", "localhost")

# ====================================================================
# 다른 서비스 포트 설정 (CORS용)
# ====================================================================
WEB_PORT = int(os.getenv("WEB_PORT", "3000"))  # Frontend 포트
GM_PORT = int(os.getenv("GM_PORT", "8001"))  # GM 서버 포트
RULE_ENGINE_PORT = int(os.getenv("RULE_ENGINE_PORT", "8002"))  # Rule Engine 포트

# ====================================================================
# CORS 허용 출처 설정
# ====================================================================


def get_cors_origins() -> list[str]:
    """CORS 허용 출처 목록 생성"""
    origins = [
        # Frontend
        f"http://localhost:{WEB_PORT}",
        f"http://127.0.0.1:{WEB_PORT}",
        # State Manager (자기 자신)
        f"http://localhost:{APP_PORT}",
        f"http://127.0.0.1:{APP_PORT}",
        # GM 서버
        f"http://localhost:{GM_PORT}",
        f"http://127.0.0.1:{GM_PORT}",
        # Rule Engine
        f"http://localhost:{RULE_ENGINE_PORT}",
        f"http://127.0.0.1:{RULE_ENGINE_PORT}",
        # Remote Host
        f"http://{REMOTE_HOST}:{APP_PORT}",
        f"http://{REMOTE_HOST}:{WEB_PORT}",
        f"http://{REMOTE_HOST}:{GM_PORT}",
        f"http://{REMOTE_HOST}:{RULE_ENGINE_PORT}",
        f"http://{REMOTE_HOST}",
    ]

    # 환경변수에서 추가 출처 읽기 (쉼표로 구분)
    extra_origins = os.getenv("EXTRA_CORS_ORIGINS", "")
    if extra_origins:
        origins.extend([origin.strip() for origin in extra_origins.split(",")])

    return origins


CORS_ORIGINS = get_cors_origins()

# ====================================================================
# PostgreSQL 연결 설정 딕셔너리 (query.py용)
# ====================================================================
DB_CONFIG = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
    "host": DB_HOST,
    "port": DB_PORT,
}