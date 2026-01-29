-- 상태 변화 기록 및 턴 전진 (함수 호출 하나로 모든 기록 완료)
SELECT record_state_change(
    :session_id, 
    :turn_type,        -- 'action', 'event', 'system' 등
    :state_changes,    -- JSONB 데이터
    :related_entities  -- UUID[] (필요 시)
);