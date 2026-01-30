from typing import Any, Dict

from fastapi import HTTPException

from state_db.infrastructure import run_sql_command, run_sql_query
from state_db.models import ActChangeResult, SequenceChangeResult
from state_db.repositories.base import BaseRepository


class ProgressRepository(BaseRepository):
    """게임 진행(Act, Sequence, Location) 관리 리포지토리"""

    # Location
    async def update_location(self, session_id: str, location: str) -> None:
        # [dev 반영] 경로 및 파일명 변경
        sql_path = self.query_dir / "MANAGE" / "location" / "location_change.sql"
        await run_sql_command(sql_path, [session_id, location])

    async def get_location(self, session_id: str) -> Dict[str, Any]:
        # [dev 반영] -r 제거
        sql_path = self.query_dir / "INQUIRY" / "Location_now.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

    async def get_progress(self, session_id: str) -> Dict[str, Any]:
        # [dev 반영] -r 제거
        sql_path = self.query_dir / "INQUIRY" / "Progress_get.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

    # Act
    async def change_act(self, session_id: str, act: int) -> ActChangeResult:
        sql_path = self.query_dir / "MANAGE" / "act" / "select_act.sql"
        await run_sql_command(sql_path, [session_id, act])
        return ActChangeResult(session_id=session_id, current_act=act)

    async def get_act(self, session_id: str) -> Dict[str, Any]:
        # [dev 반영] -r 제거
        sql_path = self.query_dir / "INQUIRY" / "Current_act.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

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

    async def get_sequence(self, session_id: str) -> Dict[str, Any]:
        # [dev 반영] -r 제거
        sql_path = self.query_dir / "INQUIRY" / "Current_sequence.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")

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

    async def limit_sequence(self, session_id: str) -> Dict[str, Any]:
        sql_path = self.query_dir / "MANAGE" / "sequence" / "limit_sequence.sql"
        result = await run_sql_query(sql_path, [session_id])
        if result:
            return result[0]
        raise HTTPException(status_code=404, detail="Session not found")
