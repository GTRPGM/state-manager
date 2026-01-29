from typing import Any, Dict, List
from uuid import UUID

from fastapi import HTTPException

from state_db.infrastructure import execute_sql_function, run_sql_command, run_sql_query
from state_db.models import (
    ActChangeResult,
    PhaseChangeResult,
    SequenceChangeResult,
    SessionInfo,
    TurnAddResult,
)
from state_db.repositories.base import BaseRepository


class SessionRepository(BaseRepository):
    # Session Lifecycle

    async def start(
        self, scenario_id: str, act: int, sequence: int, location: str
    ) -> SessionInfo:
        try:
            scenario_uuid = UUID(scenario_id)
        except (ValueError, AttributeError) as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid scenario_id: {scenario_id}"
            ) from e

        result = await execute_sql_function(
            "create_session", [scenario_uuid, act, sequence, location]
        )
        session_id = result[0].get("create_session") if result else None
        if not session_id:
            raise Exception("Failed to create session")

        return await self.get_info(session_id)

    async def end(self, session_id: str) -> None:
        sql_path = self.query_dir / "MANAGE" / "session" / "end_session.sql"
        await run_sql_command(sql_path, [session_id])

    async def pause(self, session_id: str) -> None:
        sql_path = self.query_dir / "MANAGE" / "session" / "pause_session.sql"
        await run_sql_command(sql_path, [session_id])

    async def resume(self, session_id: str) -> None:
        sql_path = self.query_dir / "MANAGE" / "session" / "resume_session.sql"
        await run_sql_command(sql_path, [session_id])

    # Session Query

    async def get_info(self, session_id: str) -> SessionInfo:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_show-r.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return SessionInfo.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Session not found")

    async def get_active_sessions(self) -> List[SessionInfo]:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_active.sql"
        results = await run_sql_query(sql_path)
        return [SessionInfo.model_validate(row) for row in results]

    async def get_all_sessions(self) -> List[SessionInfo]:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_all-r.sql"
        results = await run_sql_query(sql_path)
        return [SessionInfo.model_validate(row) for row in results]

    async def get_paused_sessions(self) -> List[SessionInfo]:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_paused-r.sql"
        results = await run_sql_query(sql_path)
        return [SessionInfo.model_validate(row) for row in results]

    async def get_ended_sessions(self) -> List[SessionInfo]:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_ended-r.sql"
        results = await run_sql_query(sql_path)
        return [SessionInfo.model_validate(row) for row in results]

    async def get_progress(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "INQUIRY" / "Progress_get-r.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

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

    async def phase_check(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "MANAGE" / "phase" / "phase_check.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

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

    async def turn_changed(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "MANAGE" / "turn" / "turn_changed.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

    # Act

    async def change_act(self, session_id: str, act: int) -> ActChangeResult:
        sql_path = self.query_dir / "MANAGE" / "act" / "select_act.sql"
        await run_sql_command(sql_path, [session_id, act])
        return ActChangeResult(session_id=session_id, current_act=act)

    async def add_act(self, session_id: str) -> ActChangeResult:
        sql_path = self.query_dir / "MANAGE" / "act" / "add_act.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return ActChangeResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Session not found")

    async def back_act(self, session_id: str) -> ActChangeResult:
        sql_path = self.query_dir / "MANAGE" / "act" / "back_act.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return ActChangeResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Session not found")

    async def get_act(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "INQUIRY" / "Current_act-r.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

    async def act_check(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "MANAGE" / "act" / "act_check.sql"
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

    async def add_sequence(self, session_id: str) -> SequenceChangeResult:
        sql_path = self.query_dir / "MANAGE" / "sequence" / "add_sequence.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return SequenceChangeResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Session not found")

    async def back_sequence(self, session_id: str) -> SequenceChangeResult:
        sql_path = self.query_dir / "MANAGE" / "sequence" / "back_sequence.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return SequenceChangeResult.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Session not found")

    async def get_sequence(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "INQUIRY" / "Current_sequence-r.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

    async def limit_sequence(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "MANAGE" / "sequence" / "limit_sequence.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")
