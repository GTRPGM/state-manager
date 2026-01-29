-- 이성(SAN) 수치 업데이트 및 이력 기록
UPDATE player 
SET state = jsonb_set(state, '{numeric, SAN}', :new_san::text::jsonb)
WHERE session_id = :session_id;

SELECT record_state_change(:session_id, 'dialogue', jsonb_build_object('change', 'san_update', 'value', :new_san));