-- --------------------------------------------------------------------
-- 8-2. Session + Phase History 조회
-- 용도: Phase 전환 흐름 분석
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.current_phase,
    ph.previous_phase,
    ph.new_phase,
    ph.turn_at_transition,
    ph.transitioned_at
FROM session s
LEFT JOIN phase_history ph ON s.session_id = ph.session_id
WHERE s.session_id = $1
ORDER BY ph.transitioned_at ASC;
