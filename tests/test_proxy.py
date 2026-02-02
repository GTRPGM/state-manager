"""Proxy module unit tests - HTTPClientManager 및 proxy_request 테스트"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from state_db.proxy.client import HTTPClientManager, proxy_request


class TestHTTPClientManager:
    """HTTPClientManager 싱글톤 테스트"""

    @pytest.fixture(autouse=True)
    async def cleanup(self):
        """각 테스트 후 클라이언트 정리"""
        yield
        await HTTPClientManager.close_client()

    @pytest.mark.asyncio
    async def test_get_client_creates_singleton(self):
        """클라이언트가 싱글톤으로 생성되는지 확인"""
        client1 = await HTTPClientManager.get_client()
        client2 = await HTTPClientManager.get_client()
        assert client1 is client2
        assert isinstance(client1, httpx.AsyncClient)

    @pytest.mark.asyncio
    async def test_close_client_clears_singleton(self):
        """클라이언트 종료 후 None으로 초기화되는지 확인"""
        await HTTPClientManager.get_client()
        assert HTTPClientManager._client is not None

        await HTTPClientManager.close_client()
        assert HTTPClientManager._client is None

    @pytest.mark.asyncio
    async def test_get_client_after_close_creates_new(self):
        """종료 후 다시 호출하면 새 클라이언트 생성"""
        client1 = await HTTPClientManager.get_client()
        await HTTPClientManager.close_client()
        client2 = await HTTPClientManager.get_client()

        # 새로운 인스턴스여야 함 (이전 것은 닫힘)
        assert client2 is not None
        assert isinstance(client2, httpx.AsyncClient)


class TestProxyRequest:
    """proxy_request 함수 테스트"""

    @pytest.fixture
    def mock_response(self):
        """Mock HTTP 응답"""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"status": "success", "data": "test"}
        return response

    @pytest.fixture
    def mock_error_response(self):
        """Mock HTTP 에러 응답"""
        response = MagicMock()
        response.status_code = 500
        response.text = "Internal Server Error"
        response.json.return_value = {"error": "Something went wrong"}
        return response

    @pytest.mark.asyncio
    async def test_successful_get_request(self, mock_response):
        """성공적인 GET 요청 테스트"""
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        with patch.object(
            HTTPClientManager,
            "get_client",
            return_value=mock_client,
        ):
            result = await proxy_request(
                method="GET",
                base_url="http://test-service",
                path="/api/test",
            )

            assert result["status"] == "success"
            mock_client.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_successful_post_request_with_json(self, mock_response):
        """JSON 바디가 있는 POST 요청 테스트"""
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        with patch.object(
            HTTPClientManager,
            "get_client",
            return_value=mock_client,
        ):
            result = await proxy_request(
                method="POST",
                base_url="http://test-service",
                path="/api/test",
                json={"key": "value"},
            )

            assert result["status"] == "success"
            call_args = mock_client.request.call_args
            assert call_args.kwargs["json"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_request_with_token(self, mock_response):
        """Bearer 토큰이 포함된 요청 테스트"""
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        with patch.object(
            HTTPClientManager,
            "get_client",
            return_value=mock_client,
        ):
            await proxy_request(
                method="GET",
                base_url="http://test-service",
                path="/api/test",
                token="my-secret-token",
            )

            call_args = mock_client.request.call_args
            assert call_args.kwargs["headers"]["Authorization"] == "Bearer my-secret-token"

    @pytest.mark.asyncio
    async def test_connection_error_raises_503(self):
        """연결 실패 시 503 HTTPException 발생"""
        from fastapi import HTTPException

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

        with patch.object(
            HTTPClientManager,
            "get_client",
            return_value=mock_client,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await proxy_request(
                    method="GET",
                    base_url="http://test-service",
                    path="/api/test",
                )

            assert exc_info.value.status_code == 503
            assert exc_info.value.detail["code"] == "SERVICE_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_timeout_raises_504(self):
        """타임아웃 시 504 HTTPException 발생"""
        from fastapi import HTTPException

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))

        with patch.object(
            HTTPClientManager,
            "get_client",
            return_value=mock_client,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await proxy_request(
                    method="GET",
                    base_url="http://test-service",
                    path="/api/test",
                )

            assert exc_info.value.status_code == 504
            assert exc_info.value.detail["code"] == "GATEWAY_TIMEOUT"

    @pytest.mark.asyncio
    async def test_upstream_error_raises_http_exception(self, mock_error_response):
        """업스트림 4xx/5xx 에러 시 HTTPException 발생"""
        from fastapi import HTTPException

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_error_response)

        with patch.object(
            HTTPClientManager,
            "get_client",
            return_value=mock_client,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await proxy_request(
                    method="GET",
                    base_url="http://test-service",
                    path="/api/test",
                )

            assert exc_info.value.status_code == 500
            assert "UPSTREAM_500" in exc_info.value.detail["code"]

    @pytest.mark.asyncio
    async def test_url_construction(self, mock_response):
        """URL이 올바르게 구성되는지 테스트"""
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        with patch.object(
            HTTPClientManager,
            "get_client",
            return_value=mock_client,
        ):
            # trailing slash와 leading slash 처리
            await proxy_request(
                method="GET",
                base_url="http://test-service/",
                path="/api/test",
            )

            call_args = mock_client.request.call_args
            assert call_args.kwargs["url"] == "http://test-service/api/test"
