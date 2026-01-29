-- [용도] 특정 세션의 Phase 전체 전환 흐름 확인 (타임라인)
-- [설명] 어떤 턴에 어떤 이유로 페이즈가 변경되었는지 순차적으로 조회합니다.
SELECT
    phase_id,
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase
WHERE session_id = :session_id
ORDER BY turn_at_transition ASC; -- 턴 번호 기준으로 정렬하는 것이 논리적으로 가장 정확함