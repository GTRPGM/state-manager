-- --------------------------------------------------------------------
-- update_user_id.sql
-- session에 user_id 매핑/업데이트
-- 용도: 기존 세션에 외부 시스템의 사용자 식별자 연결
-- --------------------------------------------------------------------

UPDATE session
SET user_id = $2
WHERE session_id = $1::uuid
RETURNING session_id, user_id;
