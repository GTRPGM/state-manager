-- --------------------------------------------------------------------
-- Session_enemy.sql
-- 세션의 Enemy 목록 조회
-- 용도: 현재 세션에 존재하는 적 목록 확인
-- API: GET /state/session/{session_id}/enemies?active_only=true
-- --------------------------------------------------------------------

SELECT
    enemy_id AS enemy_instance_id,
    scenario_enemy_id,
    name,
    description,
    (state->'numeric'->>'HP')::int AS hp,
    tags
FROM enemy
WHERE session_id = $1
  AND ($2 = false OR (state->'numeric'->>'HP')::int > 0)
ORDER BY created_at DESC;
