-- 1. 수치 업데이트 (state JSONB 내부 HP 수정)
-- $1: enemy_id, $2: session_id, $3: hp_change
UPDATE enemy
SET state = jsonb_set(
    state,
    '{numeric, HP}',
    ((state->'numeric'->>'HP')::int + $3)::text::jsonb
)
WHERE enemy_id = $1 AND session_id = $2
RETURNING
    enemy_id AS enemy_instance_id,
    (state->'numeric'->>'HP')::int AS current_hp,
    ((state->'numeric'->>'HP')::int <= 0) AS is_defeated;
