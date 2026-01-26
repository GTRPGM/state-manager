# src/gm/state_DB/configs/__init__.py
# 설정 모듈 초기화

from state_DB.configs.api_routers import API_ROUTERS
from state_DB.configs.logging_config import LOGGING_CONFIG
from state_DB.configs.setting import (
    AGE_GRAPH_NAME,
    APP_ENV,
    APP_HOST,
    APP_PORT,
    BE_ROUTER_PORT,
    CORS_ORIGINS,
    DB_CONFIG,
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
    GM_PORT,
    LLM_ROUTER_PORT,
    REDIS_PORT,
    REMOTE_HOST,
    RULE_PORT,
    SCENARIO_PORT,
    STATE_PORT,
    WEB_PORT,
)

__all__ = [
    # API Routers
    "API_ROUTERS",
    # Logging
    "LOGGING_CONFIG",
    # Server
    "APP_ENV",
    "APP_HOST",
    "APP_PORT",
    "REMOTE_HOST",
    # Ports
    "BE_ROUTER_PORT",
    "GM_PORT",
    "STATE_PORT",
    "SCENARIO_PORT",
    "RULE_PORT",
    "LLM_ROUTER_PORT",
    "WEB_PORT",
    "REDIS_PORT",
    # Database
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
    "DB_HOST",
    "DB_PORT",
    "DB_CONFIG",
    # Apache AGE
    "AGE_GRAPH_NAME",
    # CORS
    "CORS_ORIGINS",
]
