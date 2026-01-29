-- --------------------------------------------------------------------
-- Session_phase.sql
-- 세션의 현재 Phase 정보 조회
-- 용도: RuleEngine이 현재 허용되는 행동 확인
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    session_id,
    current_phase
FROM session
WHERE session_id = $1;
