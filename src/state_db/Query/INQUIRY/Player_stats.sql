-- Player_stats.sql
SELECT
    player_id, name, hp, mp, san, str, dex, int, lux, tags, created_at, updated_at
FROM player
WHERE player_id = $1;
