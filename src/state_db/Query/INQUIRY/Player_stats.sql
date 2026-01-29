-- Player_stats.sql
SELECT
    player_id,
    entity_type,
    name,
    description,
    session_id,
    state,
    relations,
    tags,
    created_at,
    updated_at
FROM player
WHERE player_id = $1::UUID;
