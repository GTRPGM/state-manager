from typing import List
from uuid import UUID

from fastapi import HTTPException

from state_db.infrastructure import execute_sql_function, run_sql_command, run_sql_query
from state_db.models import SessionInfo
from state_db.repositories.base import BaseRepository


class SessionRepository(BaseRepository):
    """세션의 생명주기 및 기본 조회를 담당하는 리포지토리"""

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

    async def get_info(self, session_id: str) -> SessionInfo:
        # [dev 반영] -r 접미사 제거
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_show.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return SessionInfo.model_validate(result[0])
        raise HTTPException(status_code=404, detail="Session not found")

    async def get_active_sessions(self) -> List[SessionInfo]:
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_active.sql"
        results = await run_sql_query(sql_path)
        return [SessionInfo.model_validate(row) for row in results]

    async def get_all_sessions(self) -> List[SessionInfo]:
        # [dev 반영] -r 접미사 제거
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_all.sql"
        results = await run_sql_query(sql_path)
        return [SessionInfo.model_validate(row) for row in results]

    async def get_paused_sessions(self) -> List[SessionInfo]:
        # [dev 반영] -r 접미사 제거
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_paused.sql"
        results = await run_sql_query(sql_path)
        return [SessionInfo.model_validate(row) for row in results]

    async def get_ended_sessions(self) -> List[SessionInfo]:
        # [dev 반영] -r 접미사 제거
        sql_path = self.query_dir / "INQUIRY" / "session" / "Session_ended.sql"
        results = await run_sql_query(sql_path)
        return [SessionInfo.model_validate(row) for row in results]
