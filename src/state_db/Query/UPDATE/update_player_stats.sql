-- --------------------------------------------------------------------
-- update_player_stats.sql
-- 플레이어 스탯 변경 (범용)
-- 용도: 여러 스탯을 동시에 업데이트
-- API: PUT /state/player/{player_id}/stats
-- --------------------------------------------------------------------

-- 여러 스탯 동시 업데이트
UPDATE player
SET
    state = jsonb_set(
        jsonb_set(
            state,
            '{numeric}',
            (state->'numeric')::jsonb || $3::jsonb
        ),
        '{boolean}',
        COALESCE((state->'boolean')::jsonb, '{}'::jsonb) || COALESCE(($3->>'boolean')::jsonb, '{}'::jsonb)
    ),
    updated_at = NOW()
WHERE player_id = $1
  AND session_id = $2
RETURNING
    player_id,
    name,
    state;

-- 파라미터:
-- $1: player_id (UUID)
-- $2: session_id (UUID)
-- $3: stat_changes (JSONB) - 변경할 스탯들
--     예: {"HP": -10, "MP": 5, "STR": 1}

-- 사용 예:
-- SELECT * FROM update_player_stats(
--     'player-uuid',
--     'session-uuid',
--     '{"HP": -10, "MP": 5, "STR": 1}'::jsonb
-- );

-- 결과:
-- player_id | name | state
-- ----------|------|--------------------------------------------------
-- uuid-123  | Hero | {"numeric": {"HP": 75, "MP": 55, "STR": 11, ...}}
