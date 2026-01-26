-- --------------------------------------------------------------------
-- 2-2. Session의 현재 Phase 정보 조회
-- 용도: RuleEngine이 현재 허용되는 행동 확인
-- --------------------------------------------------------------------

-- 현재 Phase 조회
SELECT current_phase
FROM session
WHERE session_id = $1;

-- 현재 Phase의 허용 행동 조회
SELECT get_session_allowed_actions($1);

-- 결과 예: {move, inspect, talk, use_item}
