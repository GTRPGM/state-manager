-- update_player_stats.sql
-- 플레이어 스탯 증분 업데이트 (기존 값 + 변동량)
-- $1: player_id, $2: session_id, $3: stat_changes (JSONB delta)
UPDATE player
SET
    state = jsonb_set(
        state,
        '{numeric}',
        (
            SELECT jsonb_object_agg(key, val)
            FROM (
                SELECT 
                    COALESCE(new_stats.key, old_stats.key) as key,
                    (COALESCE(old_stats.value::text::int, 0) + COALESCE(new_stats.value::text::int, 0)) as val
                FROM jsonb_each(state->'numeric') old_stats
                FULL OUTER JOIN jsonb_each($3::jsonb) new_stats ON old_stats.key = new_stats.key
            ) s
        )
    ),
    updated_at = NOW()
WHERE player_id = $1::UUID
  AND session_id = $2::UUID
RETURNING
    player_id,
    name,
    state;
