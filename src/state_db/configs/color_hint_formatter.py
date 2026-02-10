"""로그 레벨별 색상 및 HINT 강조를 지원하는 커스텀 포매터"""

import copy
import logging
from typing import Literal, Optional

from uvicorn.logging import DefaultFormatter


class ColorHintFormatter(DefaultFormatter):
    """
    메시지 본문에 'HINT:'가 있으면 노란색으로 강조하고,
    로그 레벨별로 메시지 색상을 적용하는 포매터

    색상 매핑:
    - DEBUG: cyan (청록색)
    - INFO: green (녹색) - 기본
    - WARNING: yellow (노란색)
    - ERROR: red (빨간색)
    - CRITICAL: bright_red (밝은 빨간색)
    """

    # ANSI 색상 코드
    COLORS = {
        "cyan": "\033[36m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "red": "\033[31m",
        "bright_red": "\033[91m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }

    # 로그 레벨별 메시지 색상 매핑
    LEVEL_COLORS = {
        logging.DEBUG: "cyan",
        logging.INFO: "green",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "bright_red",
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: Optional[bool] = None,
    ):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, use_colors=use_colors)

    def _apply_color(self, text: str, color_name: str) -> str:
        """텍스트에 ANSI 색상 코드 적용"""
        color_code = self.COLORS.get(color_name, "")
        reset_code = self.COLORS["reset"]
        return f"{color_code}{text}{reset_code}"

    def _highlight_hints(self, message: str) -> str:
        """메시지 내의 'HINT:'를 노란색으로 강조"""
        if "HINT:" in message:
            highlighted = self._apply_color("HINT:", "yellow")
            return message.replace("HINT:", highlighted)
        return message

    def _colorize_by_level(self, message: str, levelno: int) -> str:
        """로그 레벨에 따라 메시지 전체에 색상 적용"""
        color_name = self.LEVEL_COLORS.get(levelno)
        if color_name:
            return self._apply_color(message, color_name)
        return message

    def format(self, record: logging.LogRecord) -> str:
        # 원본 레코드 보존을 위해 복사
        record_copy = copy.copy(record)

        if self.use_colors and isinstance(record_copy.msg, str):
            # 1. HINT: 강조 처리
            record_copy.msg = self._highlight_hints(record_copy.msg)

            # 2. WARNING 이상 레벨은 메시지 전체에 색상 적용
            if record_copy.levelno >= logging.WARNING:
                record_copy.msg = self._colorize_by_level(
                    record_copy.msg, record_copy.levelno
                )

        return super().format(record_copy)
