-- 특정 행동의 허용 여부 반환 (t/f)
-- $1: session_id, $2: action_name
SELECT is_action_allowed($1, $2);