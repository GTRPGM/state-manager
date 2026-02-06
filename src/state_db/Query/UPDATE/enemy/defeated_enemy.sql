-- --------------------------------------------------------------------
-- defeated_enemy.sql
-- 적 처치 처리
-- 용도: 적을 명시적으로 처치 상태로 변경
-- API: POST /state/enemy/{enemy_instance_id}/defeat
-- --------------------------------------------------------------------

-- 적 처치 상태 업데이트 (Flattened)
UPDATE enemy
SET
    is_defeated = true,
    defeated_at = NOW(),
    hp = 0,
    updated_at = NOW()
WHERE enemy_id = $1
  AND session_id = $2
  AND is_defeated = false
RETURNING
    enemy_id,
    name,
    defeated_at,
    hp AS final_hp;
