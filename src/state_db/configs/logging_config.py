# src/gm/state_db/configs/logging_config.py
# 로깅 설정 관리

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # State Manager: False로 변경
    "formatters": {
        "default": {
            "()": "src.state_db.configs.color_hint_formatter.ColorHintFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": True,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": (
                '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
            ),
            "use_colors": True,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # stderr → stdout으로 변경
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # stderr → stdout으로 변경
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
        # State Manager 전용 로거 추가
        "state_manager": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        # asyncpg (PostgreSQL 드라이버) 로거
        "asyncpg": {
            "handlers": ["default"],
            "level": "WARNING",  # 필요 시 DEBUG로 변경
            "propagate": False,
        },
    },
}
