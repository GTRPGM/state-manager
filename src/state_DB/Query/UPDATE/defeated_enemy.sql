-- --------------------------------------------------------------------
-- defeated_enemy.sql
-- 적 처치 처리
-- 용도: 적을 명시적으로 처치 상태로 변경
-- API: POST /state/enemy/{enemy_instance_id}/defeat
-- --------------------------------------------------------------------

-- 적 처치 상태 업데이트
UPDATE enemy
SET
    is_defeated = true,
    defeated_at = NOW(),
    state = jsonb_set(
        state,
        '{numeric,HP}',
        '0'::jsonb
    ),
    updated_at = NOW()
WHERE enemy_instance_id = $1
  AND session_id = $2
  AND is_defeated = false
RETURNING
    enemy_instance_id,
    enemy_id,
    name,
    defeated_at,
    (state->'numeric'->>'HP')::int AS final_hp;

-- 파라미터:
-- $1: enemy_instance_id (UUID)
-- $2: session_id (UUID)

-- 결과 예:
-- enemy_instance_id | enemy_id | name           | defeated_at         | final_hp
-- ------------------|----------|----------------|---------------------|----------
-- uuid-abc          | 1        | Goblin Warrior | 2026-01-23 10:30:00 | 0

-- 사용 예:
-- 전투 종료 시 명시적으로 처치 상태 기록
