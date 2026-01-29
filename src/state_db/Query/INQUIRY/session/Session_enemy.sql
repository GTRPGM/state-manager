-- --------------------------------------------------------------------
-- Session_enemy.sql
-- 세션의 Enemy 목록 조회
-- $1: session_id, $2: active_only
-- --------------------------------------------------------------------

SELECT
    enemy_id AS enemy_instance_id,
    scenario_enemy_id,
    name,
    description,
    (state->'numeric'->>'HP')::int AS current_hp,
    tags,
    state
FROM enemy
WHERE session_id = $1
  AND ($2 = false OR (state->'numeric'->>'HP')::int > 0)
ORDER BY created_at DESC;
