from typing import Any, Dict

from fastapi import HTTPException

from state_db.infrastructure import run_sql_command, run_sql_query
from state_db.models import PhaseChangeResult, TurnAddResult
from state_db.repositories.base import BaseRepository


class LifecycleStateRepository(BaseRepository):
    """세부 게임 상태(Phase, Turn) 관리 리포지토리"""

    # Phase
    async def change_phase(self, session_id: str, phase: str) -> PhaseChangeResult:
        sql_path = self.query_dir / "MANAGE" / "phase" / "change_phase.sql"
        await run_sql_command(sql_path, [session_id, phase])
        return PhaseChangeResult(session_id=session_id, current_phase=phase)

    async def get_phase(self, session_id: str) -> PhaseChangeResult:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_phase.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return PhaseChangeResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Session phase not found")

    async def phase_check(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "MANAGE" / "phase" / "phase_check.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

    async def is_action_allowed(self, session_id: str, action: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "INQUIRY" / "phase" / "ALLOWED_by_phase.sql"
        result = await run_sql_query(sql_path, [session_id, action])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

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
