-- inventory_update.sql
-- GM 명령에 따라 인벤토리 상태를 업데이트
-- Apache AGE Cypher 쿼리 사용
--
-- Edge 역할:
--   PLAYER_INVENTORY: player → inventory (개별 공간)
--   EARN_ITEM: inventory → item (아이템 귀속, active 플래그)
--   USED_ITEM: inventory → item (사용 기록)
--
-- 사용법:
--   GM keyword에 따라 적절한 섹션의 쿼리 실행
--   - "획득", "습득" → EARN 섹션
--   - "사용", "소모" → USE 섹션
--   - "업데이트", "수정" → UPDATE 섹션
--
-- Parameters:
--   :player_id   - 플레이어 UUID
--   :session_id  - 세션 UUID
--   :item_id     - 아이템 UUID
--   :rule_id     - 규칙 UUID (USE 명령만)
--   :meta        - 메타데이터 JSONB (UPDATE 명령만)


-- ===============================
-- EARN: 아이템 습득 (GM으로부터 확인됨)
-- Parameters: :player_id, :session_id, :item_id
-- ===============================

-- 1️⃣ EARN_ITEM 엣지 생성 또는 활성화
SELECT *
FROM cypher('state_db', $$
  MATCH
    (i:inventory { session_id: $session_id }),
    (it:item { id: $item_id, session_id: $session_id })
  MERGE
    (i)-[r:EARN_ITEM]->(it)
  ON CREATE SET
    r.session_id = $session_id,
    r.active = true,
    r.created_at = now()
  ON MATCH SET
    r.active = true,
    r.updated_at = now()
$$) AS (v agtype);


BEGIN;

-- 1. 인벤토리에 아이템 추가 (또는 수량 증가)
INSERT INTO player_inventory (player_id, item_id, quantity)
VALUES ('player_uuid', 5, 1)
ON CONFLICT (player_id, item_id)
DO UPDATE SET quantity = player_inventory.quantity + 1;

-- 2. Turn 증가
SELECT advance_turn('session_uuid');

-- 3. Turn 상태 변경 기록
SELECT update_turn_state_changes(
    'session_uuid',
    (SELECT current_turn FROM session WHERE session_id = 'session_uuid'),
    '{"inventory_added": [5], "quantity": 1}'::jsonb,
    'earn_item'
);

COMMIT;


-- 2️⃣ 획득 메시지 생성 (선택적)
SELECT *
FROM cypher('state_db', $$
  MATCH
    (p:player { id: $player_id, session_id: $session_id }),
    (it:item { id: $item_id, session_id: $session_id })
  CREATE
    (p)-[:MESSAGE {
      id: gen_random_uuid(),
      session_id: $session_id,
      content: it.name + "을(를) 얻었습니다.",
      created_at: now()
    }]->(it)
$$) AS (v agtype);


-- ===============================
-- USE: 아이템 사용 (GM으로부터 확인됨)
-- Parameters: :player_id, :session_id, :item_id, :rule_id
-- ===============================

-- 1️⃣ EARN_ITEM 엣지 비활성화
SELECT *
FROM cypher('state_db', $$
  MATCH
    (i:inventory { session_id: $session_id })-[r:EARN_ITEM]->(it:item { id: $item_id })
  WHERE r.active = true
  SET
    r.active = false,
    r.updated_at = now()
$$) AS (v agtype);

-- 2️⃣ USED_ITEM 엣지 생성 (사용 기록 + 정보 전달)
SELECT *
FROM cypher('state_db', $$
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
FROM cypher('state_db', $$
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


-- ===============================
-- NOTES
-- ===============================
--
-- 1. EARN_ITEM 엣지는 DELETE하지 않고 active 플래그로 관리
-- 2. USED_ITEM은 사용 기록용 (인벤토리 상태 유지)
-- 3. 모든 쿼리는 session_id로 격리됨
-- 4. MERGE 사용으로 중복 실행 안전 (EARN)
-- 5. MESSAGE 엣지는 UI 알림용
--
-- TODO (향후 개선):
-- - inventory.capacity 체크 (EARN 섹션)
-- - inventory.weight_limit 체크 (EARN 섹션)
-- - 에러 처리 (OPTIONAL MATCH)
-- - 트랜잭션 래핑 (BEGIN/COMMIT)
