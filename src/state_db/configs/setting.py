# src/gm/state_db/configs/setting.py
# State Manager 설정값 관리

import os

from dotenv import load_dotenv

load_dotenv()
# ====================================================================
# PostgreSQL 데이터베이스 설정
# ====================================================================
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))

# Apache AGE 그래프 설정
AGE_GRAPH_NAME = os.getenv("AGE_GRAPH_NAME")

# ====================================================================
# 서버 설정
# ====================================================================
APP_HOST = os.getenv("APP_HOST")  # local: 127.0.0.1, prod: 0.0.0.0
APP_PORT = int(os.getenv("APP_PORT"))  # State Manager 포트 (팀 표준)
APP_ENV = os.getenv("APP_ENV")  # local, dev, prod

# ====================================================================
# 원격 호스트 설정
# ====================================================================
REMOTE_HOST = os.getenv("REMOTE_HOST")

# ====================================================================
# 팀 서비스 포트 표준 (CORS 및 서비스 간 통신용)
# ====================================================================
# 서비스 포트
BE_ROUTER_PORT = int(os.getenv("BE_ROUTER_PORT"))
GM_PORT = int(os.getenv("GM_PORT"))
STATE_PORT = APP_PORT  # 8030 (현재 서비스)
SCENARIO_PORT = int(os.getenv("SCENARIO_PORT"))
RULE_PORT = int(os.getenv("RULE_PORT"))
LLM_ROUTER_PORT = int(os.getenv("LLM_ROUTER_PORT"))
WEB_PORT = int(os.getenv("WEB_PORT"))

# 데이터베이스 포트
REDIS_PORT = int(os.getenv("REDIS_PORT"))

# ====================================================================
# CORS 허용 출처 설정
# ====================================================================


def get_cors_origins() -> list[str]:
    """CORS 허용 출처 목록 생성 (팀 표준 포트 적용)"""
    origins = [
        # Frontend (Web)
        f"http://localhost:{WEB_PORT}",
        f"http://127.0.0.1:{WEB_PORT}",
        # BE Router
        f"http://localhost:{BE_ROUTER_PORT}",
        f"http://127.0.0.1:{BE_ROUTER_PORT}",
        # GM Service
        f"http://localhost:{GM_PORT}",
        f"http://127.0.0.1:{GM_PORT}",
        # State Service (자기 자신)
        f"http://localhost:{STATE_PORT}",
        f"http://127.0.0.1:{STATE_PORT}",
        # Scenario Service
        f"http://localhost:{SCENARIO_PORT}",
        f"http://127.0.0.1:{SCENARIO_PORT}",
        # Rule Service
        f"http://localhost:{RULE_PORT}",
        f"http://127.0.0.1:{RULE_PORT}",
        # LLM Router
        f"http://localhost:{LLM_ROUTER_PORT}",
        f"http://127.0.0.1:{LLM_ROUTER_PORT}",
        # Remote Host (모든 서비스)
        f"http://{REMOTE_HOST}:{BE_ROUTER_PORT}",
        f"http://{REMOTE_HOST}:{GM_PORT}",
        f"http://{REMOTE_HOST}:{STATE_PORT}",
        f"http://{REMOTE_HOST}:{SCENARIO_PORT}",
        f"http://{REMOTE_HOST}:{RULE_PORT}",
        f"http://{REMOTE_HOST}:{LLM_ROUTER_PORT}",
        f"http://{REMOTE_HOST}:{WEB_PORT}",
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
