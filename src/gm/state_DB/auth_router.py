# src/gm/state_DB/auth_router.py
# API 키 관리 엔드포인트

from typing import List

from fastapi import APIRouter, HTTPException

from .auth import create_new_api_key, delete_api_key, list_api_keys
from .custom import WrappedResponse
from .schemas import APIKeyCreateRequest, APIKeyCreateResponse, APIKeyDeleteResponse, APIKeyInfo

# ====================================================================
# 라우터 생성
# ====================================================================

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ====================================================================
# API 키 관리 엔드포인트
# ====================================================================


@auth_router.post(
    "/api-keys",
    response_model=WrappedResponse[APIKeyCreateResponse],
    summary="API 키 생성",
    description="새로운 API 키를 생성합니다. ⚠️ 생성된 키는 한 번만 표시되므로 반드시 저장하세요.",
)
async def create_api_key(request: APIKeyCreateRequest):
    """
    새 API 키 생성

    ⚠️ **중요**: 생성된 `api_key`는 이 응답에서만 확인 가능합니다.
    반드시 안전한 곳에 저장하세요. 이후에는 조회할 수 없습니다.

    Args:
        request: API 키 이름

    Returns:
        생성된 API 키 정보 (원본 키 포함)
    """
    try:
        result = await create_new_api_key(key_name=request.key_name)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"API 키 생성 중 오류 발생: {str(e)}"
        ) from e


@auth_router.get(
    "/api-keys",
    response_model=WrappedResponse[List[APIKeyInfo]],
    summary="API 키 목록 조회",
    description="등록된 모든 API 키 목록을 조회합니다 (원본 키는 포함되지 않음).",
)
async def get_api_keys():
    """
    API 키 목록 조회

    Returns:
        모든 API 키 정보 리스트 (원본 키 제외)
    """
    try:
        result = await list_api_keys()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"API 키 조회 중 오류 발생: {str(e)}"
        ) from e


@auth_router.delete(
    "/api-keys/{api_key_id}",
    response_model=WrappedResponse[APIKeyDeleteResponse],
    summary="API 키 삭제",
    description="지정된 API 키를 비활성화합니다 (소프트 삭제).",
)
async def remove_api_key(api_key_id: str):
    """
    API 키 삭제 (비활성화)

    Args:
        api_key_id: 삭제할 API 키 ID (UUID)

    Returns:
        삭제 결과
    """
    try:
        result = await delete_api_key(api_key_id=api_key_id)

        if not result:
            raise HTTPException(
                status_code=404, detail=f"API Key ID {api_key_id}를 찾을 수 없습니다."
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"API 키 삭제 중 오류 발생: {str(e)}"
        ) from e
