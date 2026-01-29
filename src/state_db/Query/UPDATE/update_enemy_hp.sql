-- 1. 수치 업데이트 (state JSONB 내부 HP 수정)
UPDATE enemy 
SET state = jsonb_set(state, '{numeric, HP}', :new_hp::text::jsonb)
WHERE enemy_id = :enemy_id AND session_id = :session_id;

-- 2. 턴 진행 및 이력 기록 (record_state_change 함수 강제 호출)
SELECT record_state_change(
    :session_id, 
    'combat', 
    jsonb_build_object('entity_id', :enemy_id, 'change', 'hp_update', 'value', :new_hp)
);