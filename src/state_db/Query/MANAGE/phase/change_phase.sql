-- --------------------------------------------------------------------
-- 3-1. Phase 변경
-- 용도: GM 또는 RuleEngine이 Phase 전환
-- API: PUT /state/session/{session_id}/phase
-- --------------------------------------------------------------------

-- Phase 변경 함수 호출
SELECT change_phase(
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890'::UUID,  -- session_id
    'combat'::phase_type                             -- new_phase
);

-- 반환값: BOOLEAN (성공: true, 실패: false)
