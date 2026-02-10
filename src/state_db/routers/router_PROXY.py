"""Proxy router - 마이크로서비스 프록시 헬스체크 및 통신."""

from typing import Any, Dict

from fastapi import APIRouter

from state_db.custom import WrappedResponse
from state_db.proxy.services import GMProxy, RuleEngineProxy

router = APIRouter(tags=["Proxy"])


@router.get(
    "/health/proxy",
    response_model=WrappedResponse[Dict[str, Any]],
    summary="프록시 연결 상태 확인",
    description="마이크로서비스(Rule Engine, GM) 연결 상태를 확인합니다.",
)
async def proxy_health_check() -> Dict[str, Any]:
    """마이크로서비스 프록시 연결 상태 확인"""
    results: Dict[str, Any] = {"status": "healthy", "services": {}}

    # Rule Engine 체크
    try:
        await RuleEngineProxy.health_check()
        results["services"]["rule_engine"] = "connected"
    except Exception as e:
        results["services"]["rule_engine"] = f"disconnected: {type(e).__name__}"
        results["status"] = "degraded"

    # GM 체크
    try:
        await GMProxy.health_check()
        results["services"]["gm"] = "connected"
    except Exception as e:
        results["services"]["gm"] = f"disconnected: {type(e).__name__}"
        results["status"] = "degraded"

    return {"status": "success", "data": results}


@router.get(
    "/health/proxy/rule-engine",
    response_model=WrappedResponse[Dict[str, Any]],
    summary="Rule Engine 연결 확인",
)
async def rule_engine_health() -> Dict[str, Any]:
    """Rule Engine 서비스 헬스체크"""
    try:
        result = await RuleEngineProxy.health_check()
        return {"status": "success", "data": {"connected": True, "response": result}}
    except Exception as e:
        return {
            "status": "success",
            "data": {"connected": False, "error": str(e)},
        }


@router.get(
    "/health/proxy/gm",
    response_model=WrappedResponse[Dict[str, Any]],
    summary="GM 서비스 연결 확인",
)
async def gm_health() -> Dict[str, Any]:
    """GM 서비스 헬스체크"""
    try:
        result = await GMProxy.health_check()
        return {"status": "success", "data": {"connected": True, "response": result}}
    except Exception as e:
        return {
            "status": "success",
            "data": {"connected": False, "error": str(e)},
        }
