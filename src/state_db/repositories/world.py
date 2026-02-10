from typing import Any, Dict

from fastapi import HTTPException

from state_db.infrastructure import run_sql_command, run_sql_query
from state_db.models import (
    ActChangeResult,
    PhaseChangeResult,
    SequenceChangeResult,
    TurnAddResult,
)

from .base import BaseRepository


class WorldStateRepository(BaseRepository):
    """월드 상태(Phase, Turn, Act, Sequence, Location) 관리를 담당하는 Repository"""

    # Location
    async def update_location(self, session_id: str, location: str) -> None:
        sql_path = self.query_dir / "UPDATE" / "update_location-r.sql"
        await run_sql_command(sql_path, [session_id, location])

    async def get_location(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "INQUIRY" / "Location_now-r.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

    async def location_change(self, session_id: str, location: str) -> None:
        sql_path = self.query_dir / "MANAGE" / "location" / "location_change.sql"
        await run_sql_command(sql_path, [session_id, location])

    # Phase
    async def change_phase(self, session_id: str, phase: str) -> PhaseChangeResult:
        sql_path = self.query_dir / "MANAGE" / "phase" / "change_phase.sql"
        await run_sql_command(sql_path, [session_id, phase])
        return PhaseChangeResult(session_id=session_id, current_phase=phase)

    async def get_phase(self, session_id: str) -> PhaseChangeResult:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_phase-r.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return PhaseChangeResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Session phase not found")

    async def is_action_allowed(self, session_id: str, action: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "MANAGE" / "phase" / "is_action_allowed.sql"
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
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_turn-r.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return TurnAddResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Session turn not found")

    # Act
    async def change_act(self, session_id: str, act: int) -> ActChangeResult:
        sql_path = self.query_dir / "MANAGE" / "act" / "select_act.sql"
        await run_sql_command(sql_path, [session_id, act])
        return ActChangeResult(session_id=session_id, current_act=act)

    async def get_act(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "INQUIRY" / "Current_act-r.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

    # Sequence
    async def change_sequence(
        self, session_id: str, sequence: int
    ) -> SequenceChangeResult:
        sql_path = self.query_dir / "MANAGE" / "sequence" / "select_sequence.sql"
        await run_sql_command(sql_path, [session_id, sequence])
        return SequenceChangeResult(session_id=session_id, current_sequence=sequence)

    async def get_sequence(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "INQUIRY" / "Current_sequence-r.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")
