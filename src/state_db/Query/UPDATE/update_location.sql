-- --------------------------------------------------------------------
-- update_location.sql
-- 세션 위치 변경
-- 용도: 플레이어 이동으로 인한 위치 업데이트
-- API: PUT /state/session/{session_id}/location
-- --------------------------------------------------------------------

-- 위치 업데이트
UPDATE session
SET
    location = $2,
    updated_at = NOW()
WHERE session_id = $1
  AND status = 'active'
RETURNING
    session_id,
    location,
    current_phase,
    current_turn,
    updated_at;

-- 파라미터:
-- $1: session_id (UUID)
-- $2: new_location (TEXT)

-- 결과 예:
-- session_id | location     | current_phase | current_turn | updated_at
-- -----------|--------------|---------------|--------------|---------------------
-- uuid-789   | Dark Forest  | exploration   | 15           | 2026-01-23 10:45:00

-- 사용 예:
-- 플레이어가 맵을 이동할 때 호출
-- Turn 증가는 별도로 처리 (이동이 상태 변경에 해당하는 경우)
