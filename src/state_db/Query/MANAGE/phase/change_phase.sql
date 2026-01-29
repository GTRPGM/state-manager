-- --------------------------------------------------------------------
-- change_phase.sql
-- 용도: GM 또는 RuleEngine이 Phase 전환
-- API: PUT /state/session/{session_id}/phase
-- --------------------------------------------------------------------

UPDATE session
SET current_phase = $2::phase_type
WHERE session_id = $1::UUID
  AND status = 'active';
