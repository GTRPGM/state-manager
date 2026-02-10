-- 행동 결과 기록 및 턴 전진
SELECT record_state_change(
    :session_id,
    'action',
    :state_changes_json, -- 예: '{"HP": -10}'
    :related_entities    -- 예: ARRAY['uuid1', 'uuid2']
);
