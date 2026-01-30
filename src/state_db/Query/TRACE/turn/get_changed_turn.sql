-- 상태 변화 기록 및 턴 전진 (함수 호출 하나로 모든 기록 완료)
-- $1: session_id, $2: turn_type, $3: state_changes, $4: related_entities
SELECT record_state_change(
    $1,
    $2,        -- 'action', 'event', 'system' 등
    $3,        -- JSONB 데이터
    $4         -- UUID[] (필요 시)
);