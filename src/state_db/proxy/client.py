"""HTTP 클라이언트 풀 관리 - DatabaseManager 패턴 적용"""

import logging
from typing import Any, Optional

import httpx
from fastapi import HTTPException
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from state_db.configs.setting import (
    PROXY_MAX_RETRIES,
    PROXY_RETRY_MAX_WAIT,
    PROXY_RETRY_MIN_WAIT,
    PROXY_TIMEOUT,
)

logger = logging.getLogger("state_db.proxy.client")


class HTTPClientManager:
    """HTTP 클라이언트 풀 및 리소스 관리 (싱글톤)"""

    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        """HTTP 클라이언트 인스턴스 반환 (없으면 생성)"""
        if cls._client is None:
            logger.info("Initializing HTTP client pool...")
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(PROXY_TIMEOUT),
                limits=httpx.Limits(
                    max_connections=100,
                    max_keepalive_connections=20,
                ),
            )
        return cls._client

    @classmethod
    async def close_client(cls) -> None:
        """HTTP 클라이언트 종료"""
        if cls._client:
            logger.info("Closing HTTP client pool...")
            await cls._client.aclose()
            cls._client = None


def _create_retry_decorator():
    """tenacity 재시도 데코레이터 생성"""
    return retry(
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
        stop=stop_after_attempt(PROXY_MAX_RETRIES),
        wait=wait_exponential(
            multiplier=1,
            min=PROXY_RETRY_MIN_WAIT,
            max=PROXY_RETRY_MAX_WAIT,
        ),
        reraise=True,
    )


_retry_on_network_error = _create_retry_decorator()


@_retry_on_network_error
async def proxy_request(
    method: str,
    base_url: str,
    path: str,
    token: Optional[str] = None,
    params: Optional[dict] = None,
    json: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> dict[str, Any]:
    """
    마이크로서비스로 요청을 전달하는 공통 비동기 메서드

    Args:
        method: HTTP 메서드 (GET, POST, PUT, DELETE 등)
        base_url: 대상 서비스 기본 URL
        path: 요청 경로
        token: Bearer 토큰 (선택)
        params: 쿼리 파라미터 (선택)
        json: 요청 바디 (선택)
        headers: 추가 헤더 (선택)

    Returns:
        응답 JSON 데이터

    Raises:
        HTTPException: 프록시 요청 실패 시
    """
    client = await HTTPClientManager.get_client()

    # 헤더 구성
    request_headers = headers.copy() if headers else {}
    if token:
        request_headers["Authorization"] = f"Bearer {token}"

    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    try:
        response = await client.request(
            method=method.upper(),
            url=url,
            params=params,
            json=json,
            headers=request_headers,
        )

        # 4xx/5xx 에러 처리
        if response.status_code >= 400:
            detail: Any = response.text
            try:
                detail = response.json()
            except Exception:
                pass

            raise HTTPException(
                status_code=response.status_code,
                detail={
                    "status": "error",
                    "code": f"UPSTREAM_{response.status_code}",
                    "message": f"Upstream service returned {response.status_code}",
                    "detail": detail,
                },
            )

        return response.json()

    except httpx.ConnectError as e:
        logger.error(f"Connection failed to {base_url}: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "code": "SERVICE_UNAVAILABLE",
                "message": f"서비스에 연결할 수 없습니다: {base_url}",
                "detail": str(e),
            },
        )
    except httpx.TimeoutException as e:
        logger.error(f"Request timeout to {base_url}: {e}")
        raise HTTPException(
            status_code=504,
            detail={
                "status": "error",
                "code": "GATEWAY_TIMEOUT",
                "message": f"서비스 응답 시간 초과: {base_url}",
                "detail": str(e),
            },
        )
