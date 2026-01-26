-- --------------------------------------------------------------------
-- Session_enemy.sql
-- 세션의 Enemy 목록 조회
-- 용도: 현재 세션에 존재하는 적 목록 확인
-- API: GET /state/session/{session_id}/enemies?active_only=true
-- --------------------------------------------------------------------

SELECT
    enemy_instance_id,
    enemy_id,
    name,
    description,
    state,
    is_defeated,
    defeated_at,
    tags,
    created_at,
    updated_at
FROM enemy
WHERE session_id = $1
  AND ($2 = false OR is_defeated = false)  -- active_only 파라미터
ORDER BY created_at DESC;

-- 결과 예:
-- enemy_instance_id | enemy_id | name           | state              | is_defeated
-- ------------------|----------|----------------|--------------------|--------------
-- uuid-abc          | 1        | Goblin Warrior | {"HP": 25, ...}    | false
-- uuid-def          | 2        | Orc Brute      | {"HP": 0, ...}     | true
