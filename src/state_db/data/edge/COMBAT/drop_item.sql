-- drop_item.sql
-- Enemy의 아이템 드롭 정의 및 실행
-- Apache AGE Cypher 쿼리 + PostgreSQL 배열 업데이트
--
-- 두 가지 작업:
-- 1. DROP_ITEM 엣지 생성/업데이트 (Cypher)
-- 2. enemy.dropped_items 배열 업데이트 (PostgreSQL)
--
-- Parameters (정의 시):
--   :enemy_id        - Enemy UUID (enemy.enemy_id, 주의: 테이블은 enenmy_id)
--   :item_id         - Item UUID (item.item_id)
--   :session_id      - 세션 UUID
--   :drop_rate       - 드롭 확률 (선택, 기본값: 1.0)
--   :quantity        - 드롭 개수 (선택, 기본값: 1)
--   :condition       - 드롭 조건 (선택, 기본값: 'on_death')
--   :meta            - 추가 메타데이터 JSONB (선택)
--
-- Parameters (실행 시):
--   :enemy_id        - Enemy UUID
--   :session_id      - 세션 UUID
--   :current_turn    - 현재 턴 번호
--   :condition       - 드롭 조건 (선택, 기본값: 'on_death')


-- ========================================
-- 1. 드롭 테이블 정의 (MERGE 패턴)
-- ========================================
SELECT *
FROM cypher('state_db_item_logic', $$
  MATCH
    (e:enemy {enemy_id: $enemy_id, session_id: $session_id}),
    (i:item {item_id: $item_id, session_id: $session_id})
  MERGE
    (e)-[r:DROP_ITEM]->(i)
  ON CREATE SET
    r.drop_id = gen_random_uuid(),
    r.session_id = $session_id,
    r.drop_rate = coalesce($drop_rate, 1.0),
    r.quantity = coalesce($quantity, 1),
    r.condition = coalesce($condition, 'on_death'),
    r.dropped = false,
    r.dropped_turn = NULL,
    r.meta = coalesce($meta, '{}'::jsonb),
    r.created_at = now()
  ON MATCH SET
    r.drop_rate = coalesce($drop_rate, r.drop_rate),
    r.quantity = coalesce($quantity, r.quantity),
    r.condition = coalesce($condition, r.condition),
    r.meta = r.meta || coalesce($meta, '{}'::jsonb),
    r.updated_at = now()
  RETURN
    r.drop_id AS drop_id,
    r.drop_rate AS drop_rate,
    r.quantity AS quantity,
    r.condition AS condition,
    r.dropped AS dropped
$$) AS (
  drop_id agtype,
  drop_rate agtype,
  quantity agtype,
  condition agtype,
  dropped agtype
);


-- ========================================
-- 2. 드롭 실행 (확률 판정 + 배열 업데이트)
-- ========================================

-- 2-1. Cypher: DROP_ITEM 엣지 업데이트
WITH dropped_items AS (
  SELECT
    (result->'item_id')::text::uuid AS item_id,
    (result->'item_name')::text AS item_name,
    (result->'quantity')::text::integer AS quantity,
    (result->'dropped_turn')::text::integer AS dropped_turn
  FROM cypher('state_db_item_logic', format($$
    MATCH (e:enemy {enemy_id: %L, session_id: %L})-[r:DROP_ITEM]->(i:item)
    WHERE r.dropped = false
      AND r.condition = %L
      AND random() < r.drop_rate
    SET
      r.dropped = true,
      r.dropped_turn = %s,
      r.updated_at = now()
    RETURN
      i.item_id AS item_id,
      i.name AS item_name,
      r.quantity AS quantity,
      r.dropped_turn AS dropped_turn
  $$, :enemy_id, :session_id, :condition, :current_turn)) AS (result agtype)
)
-- 2-2. PostgreSQL: enemy.dropped_items 배열 업데이트
UPDATE enemy
SET
  dropped_items = array_append(dropped_items, item_id),
  updated_at = NOW()
FROM dropped_items
WHERE enemy.enenmy_id = :enemy_id  -- 주의: 테이블 오타 반영
  AND enemy.session_id = :session_id
RETURNING
  dropped_items.item_id,
  dropped_items.item_name,
  dropped_items.quantity,
  dropped_items.dropped_turn;


-- ========================================
-- 사용 예시
-- ========================================

-- 예시 1: 드롭 테이블 정의 (시나리오 초기화)
/*
SELECT *
FROM cypher('state_db_item_logic', $$
  MATCH (e:enemy {enemy_id: 'enemy-uuid'}), (i:item {item_id: 'item-uuid'})
  MERGE (e)-[r:DROP_ITEM {drop_rate: 0.7, quantity: 1}]->(i)
$$) AS (v agtype);
*/

-- 예시 2: 드롭 실행 (전투 종료 시)
/*
-- Parameters:
--   :enemy_id = 'enemy-uuid-123'
--   :session_id = 'session-uuid'
--   :current_turn = 42
--   :condition = 'on_death'

-- 실행 후:
--   1. DROP_ITEM.dropped = true
--   2. enemy.dropped_items 배열에 item_id 추가
--   3. 드롭된 아이템 목록 반환
*/
