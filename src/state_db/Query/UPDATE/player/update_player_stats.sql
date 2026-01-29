-- update_player_stats.sql
UPDATE player
SET
    state = jsonb_set(
        state,
        '{numeric}',
        (state->'numeric')::jsonb || $3::jsonb
    ),
    updated_at = NOW()
WHERE player_id = $1::UUID
  AND session_id = $2::UUID
RETURNING
    player_id,
    name,
    state;
