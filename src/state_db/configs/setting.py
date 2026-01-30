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
DB_PORT = int(os.getenv("DB_PORT", 8621))

# Apache AGE 그래프 설정
AGE_GRAPH_NAME = os.getenv("AGE_GRAPH_NAME", "state_db")

# ====================================================================
# 서버 설정
# ====================================================================
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8030))
APP_ENV = os.getenv("APP_ENV", "local")

# ====================================================================
# 데이터베이스 포트
# ====================================================================
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


# ====================================================================
# PostgreSQL 연결 설정 딕셔너리
# ====================================================================
def get_db_config() -> dict:
    """DB 설정을 호출 시점에 환경변수에서 읽어옴 (테스트 환경 지원)"""
    return {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", 8621)),
    }


# 하위 호환성을 위한 프로퍼티 (기존 코드에서 DB_CONFIG 직접 참조 시)
DB_CONFIG = get_db_config()
