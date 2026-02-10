-- --------------------------------------------------------------------
-- 9-3. 대화 행동 처리 (완전한 트랜잭션)
-- 용도: RuleEngine이 대화 판정 후 상태 적용
-- Phase: dialogue
-- --------------------------------------------------------------------

BEGIN;

-- 1. NPC 호감도 변경
INSERT INTO player_npc_relations (player_id, npc_id, affinity_score)
VALUES ('player_uuid', 'npc_uuid', 60)  -- 초기값 또는 변경값
ON CONFLICT (player_id, npc_id)
DO UPDATE SET
    affinity_score = GREATEST(0, LEAST(100, player_npc_relations.affinity_score + 10)),
    updated_at = NOW();

-- 2. 보상 획득 (선택적 - 대화 성공 시)
UPDATE player
SET state = jsonb_set(
    state,
    '{numeric,gold}',
    (COALESCE((state->'numeric'->>'gold')::int, 0) + 50)::text::jsonb
)
WHERE player_id = 'player_uuid'
  AND session_id = 'session_uuid';

-- 3. 아이템 획득 (선택적 - 퀘스트 보상)
INSERT INTO player_inventory (player_id, item_id, quantity)
VALUES ('player_uuid', 7, 1)
ON CONFLICT (player_id, item_id)
DO UPDATE SET quantity = player_inventory.quantity + 1;

-- 4. Turn 증가
SELECT advance_turn('session_uuid');

-- 5. Turn 상태 변경 기록
SELECT update_turn_state_changes(
    'session_uuid',
    (SELECT current_turn FROM session WHERE session_id = 'session_uuid'),
    '{"npc_affinity_change": 10, "gold_earned": 50, "item_received": 7}'::jsonb,
    'dialogue_action'
);

-- 6. 로그 기록 (선택적)
-- INSERT INTO play_log ...

COMMIT;
