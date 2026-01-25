# src/gm/state_DB/auth.py
# API 키 인증 및 관리 유틸리티

import hashlib
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

# ====================================================================
# API 키 보안 설정
# ====================================================================

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Query 폴더 경로
QUERY_DIR = Path(__file__).parent / "Query"


# ====================================================================
# API 키 생성 및 해싱
# ====================================================================


def generate_api_key() -> str:
    """
    새로운 API 키 생성 (32바이트 = 64자 hex)

    Returns:
        생성된 API 키 (원본, 한 번만 보여줌)
    """
    return secrets.token_hex(32)


def hash_api_key(api_key: str) -> str:
    """
    API 키를 SHA-256으로 해싱

    Args:
        api_key: 원본 API 키

    Returns:
        해시된 API 키 (DB 저장용)
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


# ====================================================================
# API 키 데이터베이스 작업
# ====================================================================


async def create_api_key_table():
    """API 키 테이블 생성 (초기화 시 한 번만 실행)"""
    from .Query.query import DatabaseManager, set_age_path

    sql_path = QUERY_DIR / "MANAGE" / "api_key" / "create_api_key_table.sql"

    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)
        await conn.execute(sql)

    print("✅ API keys table created")


async def create_new_api_key(key_name: str) -> Dict[str, Any]:
    """
    새 API 키 생성 및 DB 저장

    Args:
        key_name: API 키 이름 (식별용)

    Returns:
        {
            "api_key": "원본 키 (한 번만 표시)",
            "api_key_id": "UUID",
            "key_name": "이름",
            "created_at": "생성일"
        }
    """
    from .Query.query import DatabaseManager, set_age_path

    # 1. 원본 API 키 생성
    api_key = generate_api_key()

    # 2. 해시 생성
    key_hash = hash_api_key(api_key)

    # 3. DB에 저장
    sql_path = QUERY_DIR / "MANAGE" / "api_key" / "create_api_key.sql"

    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)
        result = await conn.fetchrow(sql, key_hash, key_name)

    # 4. 결과 반환 (원본 키 포함)
    return {
        "api_key": api_key,  # ⚠️ 원본 키는 이 한 번만 보여줌
        "api_key_id": str(result["api_key_id"]),
        "key_name": result["key_name"],
        "created_at": result["created_at"],
        "is_active": result["is_active"],
    }


async def verify_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    API 키 검증 및 정보 조회

    Args:
        api_key: 클라이언트가 보낸 API 키

    Returns:
        키 정보 dict 또는 None (유효하지 않은 경우)
    """
    from .Query.query import DatabaseManager, set_age_path

    key_hash = hash_api_key(api_key)

    sql_path = QUERY_DIR / "INQUIRY" / "get_api_key.sql"

    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)
        result = await conn.fetchrow(sql, key_hash)

    if not result:
        return None

    # 마지막 사용 시각 업데이트
    await update_api_key_last_used(key_hash)

    return {
        "api_key_id": str(result["api_key_id"]),
        "key_name": result["key_name"],
        "created_at": result["created_at"],
        "last_used_at": result["last_used_at"],
        "is_active": result["is_active"],
    }


async def update_api_key_last_used(key_hash: str):
    """API 키 마지막 사용 시각 업데이트"""
    from .Query.query import DatabaseManager, set_age_path

    sql_path = QUERY_DIR / "UPDATE" / "update_api_key_last_used.sql"

    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)
        await conn.execute(sql, key_hash)


async def list_api_keys() -> List[Dict[str, Any]]:
    """모든 API 키 목록 조회 (해시 제외)"""
    from .Query.query import DatabaseManager, set_age_path

    sql_path = QUERY_DIR / "INQUIRY" / "list_api_keys.sql"

    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)
        rows = await conn.fetch(sql)

    return [
        {
            "api_key_id": str(row["api_key_id"]),
            "key_name": row["key_name"],
            "created_at": row["created_at"],
            "last_used_at": row["last_used_at"],
            "is_active": row["is_active"],
        }
        for row in rows
    ]


async def delete_api_key(api_key_id: str) -> Optional[Dict[str, str]]:
    """
    API 키 삭제 (소프트 삭제)

    Args:
        api_key_id: 삭제할 API 키 ID

    Returns:
        삭제 결과 또는 None
    """
    from .Query.query import DatabaseManager, set_age_path

    sql_path = QUERY_DIR / "MANAGE" / "api_key" / "delete_api_key.sql"

    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()

    async with DatabaseManager.get_connection() as conn:
        await set_age_path(conn)
        result = await conn.fetchrow(sql, api_key_id)

    if not result:
        return None

    return {
        "api_key_id": str(result["api_key_id"]),
        "key_name": result["key_name"],
        "status": "deleted",
    }


# ====================================================================
# FastAPI 의존성 (Depends에서 사용)
# ====================================================================


async def get_api_key(api_key: str = Security(api_key_header)) -> Dict[str, Any]:
    """
    FastAPI Depends로 사용할 API 키 검증 함수

    Usage:
        @app.get("/protected", dependencies=[Depends(get_api_key)])
        async def protected_route():
            ...

    Raises:
        HTTPException: API 키가 유효하지 않은 경우
    """
    key_info = await verify_api_key(api_key)

    if not key_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid or inactive API key",
            headers={"WWW-Authenticate": API_KEY_NAME},
        )

    return key_info
