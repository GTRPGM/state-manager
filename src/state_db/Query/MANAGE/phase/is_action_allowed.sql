-- --------------------------------------------------------------------
-- is_action_allowed.sql
-- 현재 페이즈에서 특정 행동이 허용되는지 확인
-- $1: session_id, $2: action_type
-- --------------------------------------------------------------------

SELECT
    $2 = ANY(pr.allowed_actions) AS is_allowed,
    s.current_phase,
    pr.allowed_actions
FROM session s
JOIN phase_rules pr ON s.current_phase = pr.phase
WHERE s.session_id = $1;
