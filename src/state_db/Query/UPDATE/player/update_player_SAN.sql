-- 이성(SAN) 수치 업데이트 및 이력 기록
-- $1: session_id, $2: new_san
UPDATE player
SET state = jsonb_set(state, '{numeric, SAN}', $2::text::jsonb)
WHERE session_id = $1::uuid;

SELECT record_state_change($1::uuid, 'dialogue', jsonb_build_object('change', 'san_update', 'value', $2));
