-- 특정 세션의 Turn 이력 조회 (전체)
-- 용도: 게임 진행 중 Turn별 상태 변경 확인
-- API: GET /trace/session/{session_id}/turns

SELECT
    history_id,
    session_id,
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    related_entities,
    created_at
FROM turn_history
WHERE session_id = $1
ORDER BY turn_number ASC;
