-- update_player_stats.sql
-- 플레이어 스탯 증분 업데이트 (기존 값 + 변동량)
-- $1: player_id, $2: session_id, $3: stat_changes (JSONB delta)
UPDATE player
SET
    str = LEAST(99, GREATEST(0, COALESCE(str, 0)
        + COALESCE(($3::jsonb ->> 'STR')::int, ($3::jsonb ->> 'str')::int, 0))),
    dex = LEAST(99, GREATEST(0, COALESCE(dex, 0)
        + COALESCE(($3::jsonb ->> 'DEX')::int, ($3::jsonb ->> 'dex')::int, 0))),
    int = LEAST(99, GREATEST(0, COALESCE(int, 0)
        + COALESCE(($3::jsonb ->> 'INT')::int, ($3::jsonb ->> 'int')::int, 0))),
    lux = LEAST(99, GREATEST(0, COALESCE(lux, 0)
        + COALESCE(($3::jsonb ->> 'LUX')::int, ($3::jsonb ->> 'lux')::int, 0))),
    hp = LEAST(100, GREATEST(0, COALESCE(hp, 0)
        + COALESCE(($3::jsonb ->> 'HP')::int, ($3::jsonb ->> 'hp')::int, 0))),
    mp = LEAST(99, GREATEST(0, COALESCE(mp, 0)
        + COALESCE(($3::jsonb ->> 'MP')::int, ($3::jsonb ->> 'mp')::int, 0))),
    san = LEAST(99, GREATEST(0, COALESCE(san, 0)
        + COALESCE(($3::jsonb ->> 'SAN')::int, ($3::jsonb ->> 'san')::int, 0))),
    updated_at = NOW()
WHERE player_id = $1::UUID
  AND session_id = $2::UUID
RETURNING
    player_id,
    name;
