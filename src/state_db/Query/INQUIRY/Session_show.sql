-- --------------------------------------------------------------------
-- 2-4. Session 기본 통계
-- 용도: 대시보드 표시
-- --------------------------------------------------------------------

SELECT
    session_id,
    current_phase,
    current_turn,

    -- 세션 진행 시간
    NOW() - started_at AS session_duration,

    -- Phase별 Turn 수 (서브쿼리)
    (SELECT COUNT(*) FROM turn_history th
     WHERE th.session_id = s.session_id
       AND th.phase_at_turn = 'combat') AS combat_turns,

    (SELECT COUNT(*) FROM turn_history th
     WHERE th.session_id = s.session_id
       AND th.phase_at_turn = 'exploration') AS exploration_turns
FROM session s
WHERE session_id = $1;
