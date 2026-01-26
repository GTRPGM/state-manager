-- --------------------------------------------------------------------
-- 6-1. Location 업데이트
-- 용도: 플레이어 위치 변경
-- API: PUT /state/session/{session_id}/location
-- --------------------------------------------------------------------

UPDATE session
SET location = $2  -- new_location
WHERE session_id = $1
  AND status = 'active';

-- 파라미터:
-- $1: session_id
-- $2: 'Forest Entrance'
