-- drop_item.cypher
-- Enemy가 드롭하는 Item 정의
--
-- 관계 타입: DROP_ITEM
-- 방향: enemy → item (단방향)
--
-- 속성:
--   - drop_id: UUID (고유 식별자)
--   - session_id: UUID (세션 격리)
--   - drop_rate: FLOAT (드롭 확률 0.0 ~ 1.0)
--   - quantity: INTEGER (드롭 개수)
--   - condition: TEXT (드롭 조건: 'on_death', 'on_defeat' 등)
--   - dropped: BOOLEAN (실제 드롭 여부, 기본값 false)
--   - dropped_turn: INTEGER (드롭된 턴 번호, NULL이면 아직 드롭 안됨)
--   - meta: JSONB (추가 메타데이터)
--   - created_at: TIMESTAMP
--   - updated_at: TIMESTAMP
--
-- 참고:
--   - enemy.enemy_id 사용 (오타 주의: 테이블에는 enenmy_id)
--   - item.item_id 사용
--   - enemy.dropped_items 배열에도 추가 필요

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
