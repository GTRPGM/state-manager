-- update_player_hp.sql
-- CHECK (hp >= 0) 제약에 맞게 GREATEST로 하한 클램핑
UPDATE player
SET hp = GREATEST(hp + $3, 0),
    updated_at = NOW()
WHERE player_id = $1 AND session_id = $2
RETURNING player_id, hp as current_hp;
