-- --------------------------------------------------------------------
-- update_player_hp.sql
-- 플레이어 HP 변경
-- 용도: 전투, 아이템 사용, 회복 등으로 HP 변경
-- API: PUT /state/player/{player_id}/hp
-- --------------------------------------------------------------------

-- HP 변경 (JSONB 업데이트)
UPDATE player
SET
    state = jsonb_set(
        state,
        '{numeric,HP}',
        (COALESCE((state->'numeric'->>'HP')::int, 0) + $3)::text::jsonb
    ),
    updated_at = NOW()
WHERE player_id = $1
  AND session_id = $2
RETURNING
    player_id,
    name,
    (state->'numeric'->>'HP')::int AS current_hp,
    (state->'numeric'->>'max_hp')::int AS max_hp,
    $3 AS hp_change;

-- 파라미터:
-- $1: player_id (UUID)
-- $2: session_id (UUID)
-- $3: hp_change (INTEGER) - 양수: 회복, 음수: 피해
-- $4: reason (VARCHAR) - 변경 사유 (combat, item, rest 등) - 선택적, 로그용

-- 결과 예:
-- player_id | name | current_hp | max_hp | hp_change
-- ----------|------|------------|--------|----------
-- uuid-123  | Hero | 75         | 100    | -25

-- 사용 예:
-- UPDATE player SET state = jsonb_set(state, '{numeric,HP}', '75') WHERE player_id = 'uuid';
