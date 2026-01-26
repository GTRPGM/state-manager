-- --------------------------------------------------------------------
-- update_enemy_hp.sql
-- 적 HP 변경
-- 용도: 전투로 인한 적 HP 감소
-- API: PUT /state/enemy/{enemy_instance_id}/hp
-- --------------------------------------------------------------------

-- HP 변경 및 처치 상태 자동 업데이트
UPDATE enemy
SET
    state = jsonb_set(
        state,
        '{numeric,HP}',
        GREATEST(0, (COALESCE((state->'numeric'->>'HP')::int, 0) + $3))::text::jsonb
    ),
    is_defeated = CASE
        WHEN (COALESCE((state->'numeric'->>'HP')::int, 0) + $3) <= 0 THEN true
        ELSE is_defeated
    END,
    defeated_at = CASE
        WHEN (COALESCE((state->'numeric'->>'HP')::int, 0) + $3) <= 0 AND is_defeated = false
            THEN NOW()
        ELSE defeated_at
    END,
    updated_at = NOW()
WHERE enemy_instance_id = $1
  AND session_id = $2
RETURNING
    enemy_instance_id,
    enemy_id,
    name,
    (state->'numeric'->>'HP')::int AS current_hp,
    (state->'numeric'->>'max_hp')::int AS max_hp,
    is_defeated,
    defeated_at;

-- 파라미터:
-- $1: enemy_instance_id (UUID)
-- $2: session_id (UUID)
-- $3: hp_change (INTEGER) - 보통 음수 (피해량)

-- 결과 예:
-- enemy_instance_id | name           | current_hp | max_hp | is_defeated
-- ------------------|----------------|------------|--------|-------------
-- uuid-abc          | Goblin Warrior | 15         | 30     | false
-- uuid-def          | Orc Brute      | 0          | 50     | true
