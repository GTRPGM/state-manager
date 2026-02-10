-- --------------------------------------------------------------------
-- 9-2. 탐색 행동 처리 (완전한 트랜잭션)
-- 용도: RuleEngine이 탐색 판정 후 상태 적용
-- Phase: exploration
-- --------------------------------------------------------------------

BEGIN;

-- 1. 위치 이동
UPDATE session
SET location = 'new_location'
WHERE session_id = 'session_uuid';

-- 2. 아이템 발견 (선택적)
INSERT INTO player_inventory (player_id, item_id, quantity)
VALUES ('player_uuid', 3, 1)  -- 발견한 아이템
ON CONFLICT (player_id, item_id)
DO UPDATE SET quantity = player_inventory.quantity + 1;

-- 3. MP 소모 (이동 비용)
UPDATE player
SET state = jsonb_set(
    state,
    '{numeric,MP}',
    (COALESCE((state->'numeric'->>'MP')::int, 0) - 5)::text::jsonb
)
WHERE player_id = 'player_uuid'
  AND session_id = 'session_uuid';

-- 4. Turn 증가
SELECT advance_turn('session_uuid');

-- 5. Turn 상태 변경 기록
SELECT update_turn_state_changes(
    'session_uuid',
    (SELECT current_turn FROM session WHERE session_id = 'session_uuid'),
    '{"location_changed": "new_location", "mp_used": 5, "item_found": 3}'::jsonb,
    'exploration_action'
);

-- 6. 로그 기록 (선택적)
-- INSERT INTO play_log ...

COMMIT;
