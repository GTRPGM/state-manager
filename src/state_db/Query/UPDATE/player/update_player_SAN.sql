-- 이성(SAN) 수치 업데이트 및 이력 기록 (증분 방식)
-- $1: session_id, $2: san_change
UPDATE player
SET state = jsonb_set(
    state, 
    '{numeric, SAN}', 
    (COALESCE((state->'numeric'->>'SAN')::int, 0) + $2::int)::text::jsonb
)
WHERE session_id = $1::uuid;

-- 변경 내역 기록
SELECT record_state_change($1::uuid, 'system', jsonb_build_object('change', 'san_delta', 'value', $2::int));
