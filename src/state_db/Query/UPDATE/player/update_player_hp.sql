-- update_player_hp.sql
-- 플레이어 HP 변경
-- API: PUT /state/player/{player_id}/hp
-- --------------------------------------------------------------------

UPDATE player
SET
    state = jsonb_set(
        state,
        '{numeric,HP}',
        to_jsonb(COALESCE((state->'numeric'->>'HP')::int, 100) + $3::int)
    ),
    updated_at = NOW()
WHERE player_id = $1::UUID
  AND session_id = $2::UUID
RETURNING
    player_id,
    name,
    (state->'numeric'->>'HP')::int AS current_hp,
    COALESCE((state->'numeric'->>'max_hp')::int, 100) AS max_hp,
    $3::int AS hp_change;
