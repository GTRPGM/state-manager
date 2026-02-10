-- relation.cypher
-- 모든 엔티티 간 범용 관계 정의
--
-- 관계 타입: RELATION
-- 방향: 단방향 (A → B, B → A는 별도 엣지)
--
-- 사용 가능한 엔티티:
--   - player ↔ npc
--   - player ↔ enemy
--   - npc ↔ npc
--   - enemy ↔ enemy
--   - 기타 모든 조합
--
-- 속성:
--   - relation_id: UUID (고유 식별자, 시나리오 전달)
--   - session_id: UUID (세션 격리)
--   - relation_type: TEXT (관계 유형)
--     * friendly (우호)
--     * neutral (중립)
--     * hostile (적대)
--     * ownership (소유)
--     * 향후 확장 가능
--   - affinity: INTEGER (호감도: 0~100, 기본값: 0)
--   - active: BOOLEAN (등장/퇴장 상태, 기본값: true)
--   - meta: JSONB (추가 메타데이터)
--     * created_turn: INTEGER (생성된 턴)
--     * deactivated_turn: INTEGER (비활성화된 턴, NULL이면 활성 상태)
--   - created_at: TIMESTAMP
--   - updated_at: TIMESTAMP
--
-- 생명주기:
--   - 생성: 시나리오 전달 시 즉시 생성
--   - 퇴장: active = false (엣지 유지)
--   - 세션 종료: 완전 삭제
--
-- Parameters:
--   $relation_id      - 관계 UUID (시나리오 전달)
--   $from_entity_id   - 출발 엔티티 ID
--   $from_entity_type - 출발 엔티티 타입 (player/npc/enemy)
--   $to_entity_id     - 도착 엔티티 ID
--   $to_entity_type   - 도착 엔티티 타입 (player/npc/enemy)
--   $session_id       - 세션 UUID
--   $relation_type    - 관계 유형 (시나리오 전달)
--   $affinity         - 호감도 (시나리오 전달, 선택, 기본값: 0)
--   $active           - 활성 상태 (선택, 기본값: true)
--   $current_turn     - 현재 턴 번호
--   $meta             - 추가 메타데이터 (선택)

MATCH
  (from_node {session_id: $session_id}),
  (to_node {session_id: $session_id})
WHERE
  (from_node:player AND from_node.id = $from_entity_id) OR
  (from_node:npc AND from_node.npc_id = $from_entity_id) OR
  (from_node:enemy AND from_node.enemy_id = $from_entity_id)
AND
  (to_node:player AND to_node.id = $to_entity_id) OR
  (to_node:npc AND to_node.npc_id = $to_entity_id) OR
  (to_node:enemy AND to_node.enemy_id = $to_entity_id)
MERGE
  (from_node)-[r:RELATION]->(to_node)
ON CREATE SET
  r.relation_id = $relation_id,
  r.session_id = $session_id,
  r.relation_type = $relation_type,
  r.affinity = coalesce($affinity, 0),
  r.active = coalesce($active, true),
  r.meta = coalesce($meta, jsonb_build_object(
    'created_turn', $current_turn
  )),
  r.created_at = now()
ON MATCH SET
  r.relation_type = coalesce($relation_type, r.relation_type),
  r.affinity = coalesce($affinity, r.affinity),
  r.active = coalesce($active, r.active),
  r.meta = CASE
    WHEN $active = false AND r.active = true THEN
      jsonb_set(r.meta, '{deactivated_turn}', to_jsonb($current_turn))
    WHEN $active = true AND r.active = false THEN
      jsonb_set(r.meta, '{reactivated_turn}', to_jsonb($current_turn))
    ELSE
      r.meta
  END || coalesce($meta, '{}'::jsonb),
  r.updated_at = now()
RETURN
  r.relation_id AS relation_id,
  r.relation_type AS relation_type,
  r.affinity AS affinity,
  r.active AS active,
  r.meta AS meta
