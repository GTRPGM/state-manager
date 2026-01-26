# src/gm/state_db/custom.py
# CustomStatus, CommonResponse, WrappedResponse, CustomJSONResponse 정의

from enum import Enum
from typing import Any, Dict, Generic, Optional, TypeVar

from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

# ====================================================================
# 응답 상태 Enum
# ====================================================================


class CustomStatus(str, Enum):
    """API 응답 상태 코드"""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


# ====================================================================
# 공통 응답 모델
# ====================================================================


class CommonResponse(BaseModel):
    """
    모든 API 응답의 기본 구조

    Examples:
        성공: {"status": "success", "data": {...}, "message": "Operation completed"}
        실패: {"status": "error", "data": null, "message": "Error details"}
    """

    status: CustomStatus = Field(
        default=CustomStatus.SUCCESS, description="응답 상태 (success/error/warning)"
    )
    data: Optional[object] = Field(default=None, description="실제 응답 데이터")
    message: Optional[str] = Field(default=None, description="사용자에게 보여줄 메시지")

    model_config = ConfigDict(use_enum_values=True)  # Enum을 문자열로 직렬화


# ====================================================================
# Swagger 문서화용 제네릭 래퍼
# ====================================================================

T = TypeVar("T")  # 제네릭 타입 변수


class WrappedResponse(BaseModel, Generic[T]):
    """
    Swagger에 표시될 전체 구조 모델
    response_model에서 사용하여 타입 안전성 확보

    Usage:
        @app.get("/users", response_model=WrappedResponse[List[UserSchema]])
        async def get_users():
            ...
    """

    status: CustomStatus = CustomStatus.SUCCESS
    data: T
    message: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)


# ====================================================================
# 커스텀 JSON 응답 클래스 (팀 표준)
# ====================================================================


class CustomJSONResponse(JSONResponse):
    """
    모든 성공 응답을 {status: "success", data: ..., message: ...}
    포맷으로 자동 래핑하는 커스텀 응답 클래스.

    BE-router, rule-engine, state-manager 공통 사용 표준
    """

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, Any]] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
        # 커스텀 필드를 추가하여 message와 status를 전달받을 수 있도록 합니다.
        response_message: Optional[str] = None,
        response_status: CustomStatus = CustomStatus.SUCCESS,
    ) -> None:
        # content가 이미 CommonResponse 객체인 경우 (에러 핸들러 등) 처리
        if isinstance(content, dict) and "status" in content:
            final_content = content
        else:
            # 전달받은 데이터를 CommonResponse 구조의 data 필드에 래핑
            wrapped_content = CommonResponse(
                status=response_status,
                data=content,
                message=response_message,
            )
            final_content = wrapped_content.model_dump(by_alias=True, exclude_none=True)

        super().__init__(
            content=final_content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )
