-- ===============================
-- USE: 아이템 사용 (GM으로부터 확인됨)
-- Parameters: :player_id, :session_id, :item_id, :rule_id
-- ===============================

-- 1️⃣ EARN_ITEM 엣지 비활성화
SELECT *
FROM cypher('state_db_item_logic', $$
  MATCH
    (i:inventory { session_id: $session_id })-[r:EARN_ITEM]->(it:item { id: $item_id })
  WHERE r.active = true
  SET
    r.active = false,
    r.updated_at = now()
$$) AS (v agtype);

-- 2️⃣ USED_ITEM 엣지 생성 (사용 기록 + 정보 전달)
SELECT *
FROM cypher('state_db_item_logic', $$
  MATCH
    (i:inventory { session_id: $session_id }),
    (it:item { id: $item_id, session_id: $session_id })
  CREATE
    (i)-[:USED_ITEM {
      id: gen_random_uuid(),
      session_id: $session_id,
      rule_id: $rule_id,
      created_at: now(),
      success: true
    }]->(it)
$$) AS (v agtype);


BEGIN;

-- 1. 인벤토리에 아이템 추가 (또는 수량 증가)
INSERT INTO player_inventory (player_id, item_id, quantity)
VALUES ('player_uuid', 5, 1)
ON CONFLICT (player_id, item_id)
DO UPDATE SET quantity = player_inventory.quantity - 1;

-- 2. Turn 증가
SELECT advance_turn('session_uuid');

-- 3. Turn 상태 변경 기록
SELECT update_turn_state_changes(
    'session_uuid',
    (SELECT current_turn FROM session WHERE session_id = 'session_uuid'),
    '{"inventory_lost": [5], "quantity": 1}'::jsonb,
    'use_item'
);

COMMIT;


-- 3️⃣ 사용 메시지 생성 (선택적)
SELECT *
FROM cypher('state_db_item_logic', $$
  MATCH
    (p:player { id: $player_id, session_id: $session_id }),
    (it:item { id: $item_id, session_id: $session_id })
  CREATE
    (p)-[:MESSAGE {
      id: gen_random_uuid(),
      session_id: $session_id,
      content: it.name + "을(를) 사용했습니다.",
      created_at: now()
    }]->(it)
$$) AS (v agtype);


-- ===============================
-- UPDATE: 아이템 메타데이터 업데이트
-- Parameters: :item_id, :session_id, :meta
-- ===============================

-- PostgreSQL 테이블 직접 업데이트 (AGE 그래프가 아님)
UPDATE item
SET
    meta = meta || :meta::jsonb,
    updated_at = NOW()
WHERE
    item_id = :item_id
    AND session_id = :session_id;
