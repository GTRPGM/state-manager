-- update_enemy_hp.sql
-- $1: enemy_id (UUID), $2: session_id, $3: hp_change
-- CHECK (hp >= 0) 제약에 맞게 GREATEST로 하한 클램핑
UPDATE enemy
SET hp = GREATEST(hp + $3, 0),
    updated_at = NOW()
WHERE enemy_id = $1 AND session_id = $2
RETURNING
    enemy_id,
    hp AS current_hp,
    is_defeated;
