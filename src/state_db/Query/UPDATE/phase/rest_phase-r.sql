-- --------------------------------------------------------------------
-- 9-4. 휴식 행동 처리 (완전한 트랜잭션)
-- 용도: RuleEngine이 휴식 판정 후 상태 적용
-- Phase: rest
-- --------------------------------------------------------------------

BEGIN;

-- 1. HP/MP 회복
UPDATE player
SET state = jsonb_set(
    jsonb_set(
        state,
        '{numeric,HP}',
        LEAST(
            (state->'numeric'->>'HP')::int + 30,
            (state->'numeric'->>'max_hp')::int
        )::text::jsonb
    ),
    '{numeric,MP}',
    LEAST(
        (state->'numeric'->>'MP')::int + 20,
        (state->'numeric'->>'max_mp')::int
    )::text::jsonb
)
WHERE player_id = 'player_uuid'
  AND session_id = 'session_uuid';

-- 2. 상태이상 회복 (선택적)
UPDATE player
SET state = jsonb_set(
    state,
    '{boolean}',
    '{}'::jsonb  -- 모든 상태이상 제거
)
WHERE player_id = 'player_uuid'
  AND session_id = 'session_uuid';

-- 3. 소모품 사용 (선택적 - 회복 아이템)
UPDATE player_inventory
SET quantity = quantity - 1
WHERE player_id = 'player_uuid'
  AND item_id = 1  -- 회복 아이템
  AND quantity > 0;

-- 4. 시간 경과 기록 (선택적)
-- UPDATE session SET time_passed = time_passed + INTERVAL '1 hour'

-- 5. Turn 증가
SELECT advance_turn('session_uuid');

-- 6. Turn 상태 변경 기록
SELECT update_turn_state_changes(
    'session_uuid',
    (SELECT current_turn FROM session WHERE session_id = 'session_uuid'),
    '{"hp_recovered": 30, "mp_recovered": 20, "status_cleared": true}'::jsonb,
    'rest_action'
);

-- 7. 로그 기록 (선택적)
-- INSERT INTO play_log ...

COMMIT;
