-- update_player_hp.sql
UPDATE player
SET hp = hp + $3,
    updated_at = NOW()
WHERE player_id = $1 AND session_id = $2
RETURNING player_id, hp as current_hp;
