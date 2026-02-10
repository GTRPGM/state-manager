-- --------------------------------------------------------------------
-- 9-1. 전투 행동 처리 (완전한 트랜잭션)
-- 용도: RuleEngine이 전투 판정 후 상태 적용
-- Phase: combat
-- --------------------------------------------------------------------

BEGIN;

-- 1. 플레이어 HP 감소 (적의 공격)
UPDATE player
SET state = jsonb_set(
    state,
    '{numeric,HP}',
    (COALESCE((state->'numeric'->>'HP')::int, 0) - 10)::text::jsonb
)
WHERE player_id = 'player_uuid'
  AND session_id = 'session_uuid';

-- 2. 적 HP 감소 (플레이어의 공격)
UPDATE enemy
SET state = jsonb_set(
    state,
    '{numeric,HP}',
    GREATEST(0, (COALESCE((state->'numeric'->>'HP')::int, 0) - 20))::text::jsonb
),
is_defeated = CASE
    WHEN (COALESCE((state->'numeric'->>'HP')::int, 0) - 20) <= 0 THEN true
    ELSE is_defeated
END,
defeated_at = CASE
    WHEN (COALESCE((state->'numeric'->>'HP')::int, 0) - 20) <= 0 AND is_defeated = false
        THEN NOW()
    ELSE defeated_at
END
WHERE enemy_instance_id = 'enemy_uuid'
  AND session_id = 'session_uuid';

-- 3. MP 소모 (스킬 사용 시)
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
    '{"player_hp": -10, "player_mp": -5, "enemy_hp": -20}'::jsonb,
    'combat_action'
);

-- 6. 로그 기록 (선택적)
-- INSERT INTO play_log ...

COMMIT;
