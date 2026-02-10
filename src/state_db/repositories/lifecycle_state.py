from typing import Any, Dict

from fastapi import HTTPException

from state_db.infrastructure import run_sql_query
from state_db.models import TurnAddResult
from state_db.repositories.base import BaseRepository


class LifecycleStateRepository(BaseRepository):
    """세부 게임 상태(Turn) 관리 리포지토리"""

    # Turn
    async def add_turn(self, session_id: str) -> TurnAddResult:
        sql_path = self.query_dir / "MANAGE" / "turn" / "add_turn.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return TurnAddResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Session not found")

    async def get_turn(self, session_id: str) -> TurnAddResult:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_turn.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return TurnAddResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Session turn not found")

    async def turn_changed(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "MANAGE" / "turn" / "turn_changed.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")
