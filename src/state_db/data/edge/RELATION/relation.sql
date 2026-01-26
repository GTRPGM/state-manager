-- relation.sql
-- 범용 RELATION 엣지 생성/업데이트/조회
-- Apache AGE Cypher 쿼리 사용
--
-- 용도:
--   1. 시나리오 전달 시 관계 생성
--   2. 등장/퇴장 처리 (active 플래그)
--   3. 호감도 업데이트 (affinity)
--   4. 세션 종료 시 완전 삭제
--
-- Parameters:
--   :relation_id      - 관계 UUID (시나리오 전달)
--   :from_entity_id   - 출발 엔티티 ID
--   :from_entity_type - 출발 엔티티 타입 (player/npc/enemy)
--   :to_entity_id     - 도착 엔티티 ID
--   :to_entity_type   - 도착 엔티티 타입 (player/npc/enemy)
--   :session_id       - 세션 UUID
--   :relation_type    - 관계 유형 (friendly/neutral/hostile/ownership)
--   :affinity         - 호감도 (0~100, 선택, 기본값: 0)
--   :active           - 활성 상태 (선택, 기본값: true)
--   :current_turn     - 현재 턴 번호
--   :meta             - 추가 메타데이터 JSONB (선택)
--
-- 반환값:
--   relation_id, relation_type, affinity, active, meta


-- ========================================
-- 1. 관계 생성/업데이트 (MERGE)
-- ========================================
SELECT *
FROM cypher('state_db_actor_logic', $$
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
$$) AS (
  relation_id agtype,
  relation_type agtype,
  affinity agtype,
  active agtype,
  meta agtype
);


-- ========================================
-- 2. 특정 엔티티의 모든 관계 조회
-- ========================================
-- 특정 엔티티가 출발점인 모든 관계
SELECT *
FROM cypher('state_db_actor_logic', $$
  MATCH
    (from_node {session_id: $session_id})-[r:RELATION]->(to_node)
  WHERE
    (from_node:player AND from_node.id = $entity_id) OR
    (from_node:npc AND from_node.npc_id = $entity_id) OR
    (from_node:enemy AND from_node.enemy_id = $entity_id)
  RETURN
    r.relation_id AS relation_id,
    r.relation_type AS relation_type,
    r.affinity AS affinity,
    r.active AS active,
    to_node AS target_entity
$$) AS (
  relation_id agtype,
  relation_type agtype,
  affinity agtype,
  active agtype,
  target_entity agtype
);


-- ========================================
-- 3. 호감도만 업데이트
-- ========================================
SELECT *
FROM cypher('state_db_actor_logic', $$
  MATCH
    (from_node {session_id: $session_id})-[r:RELATION]->(to_node {session_id: $session_id})
  WHERE
    r.relation_id = $relation_id
  SET
    r.affinity = $affinity,
    r.updated_at = now()
  RETURN
    r.relation_id AS relation_id,
    r.affinity AS affinity
$$) AS (
  relation_id agtype,
  affinity agtype
);


-- ========================================
-- 4. 퇴장 처리 (active = false)
-- ========================================
SELECT *
FROM cypher('state_db_actor_logic', $$
  MATCH
    (from_node {session_id: $session_id})-[r:RELATION]->(to_node {session_id: $session_id})
  WHERE
    r.relation_id = $relation_id
  SET
    r.active = false,
    r.meta = jsonb_set(r.meta, '{deactivated_turn}', to_jsonb($current_turn)),
    r.updated_at = now()
  RETURN
    r.relation_id AS relation_id,
    r.active AS active
$$) AS (
  relation_id agtype,
  active agtype
);


-- ========================================
-- 5. 재등장 처리 (active = true)
-- ========================================
SELECT *
FROM cypher('state_db_actor_logic', $$
  MATCH
    (from_node {session_id: $session_id})-[r:RELATION]->(to_node {session_id: $session_id})
  WHERE
    r.relation_id = $relation_id
  SET
    r.active = true,
    r.meta = jsonb_set(r.meta, '{reactivated_turn}', to_jsonb($current_turn)),
    r.updated_at = now()
  RETURN
    r.relation_id AS relation_id,
    r.active AS active
$$) AS (
  relation_id agtype,
  active agtype
);


-- ========================================
-- 6. 세션 종료 시 완전 삭제
-- ========================================
SELECT *
FROM cypher('state_db_actor_logic', $$
  MATCH
    ()-[r:RELATION {session_id: $session_id}]->()
  DELETE r
  RETURN count(r) AS deleted_count
$$) AS (
  deleted_count agtype
);


-- ========================================
-- 사용 예시
-- ========================================

-- 예시 1: 시나리오 전달 - player와 npc 관계 생성
/*
-- Parameters:
--   :relation_id = 'relation-uuid-123' (시나리오에서 생성)
--   :from_entity_id = 'player-uuid'
--   :to_entity_id = 'npc-uuid'
--   :session_id = 'session-uuid'
--   :relation_type = 'friendly'
--   :affinity = 30
--   :active = true (기본값)
--   :current_turn = 1

-- 쿼리 실행: 섹션 1번 사용
-- 결과: relation_id, relation_type='friendly', affinity=30, active=true
*/

-- 예시 2: 호감도 증가 (전투 후 동료 NPC)
/*
-- Parameters:
--   :relation_id = 'relation-uuid-123'
--   :affinity = 45 (30 → 45로 증가)

-- 쿼리 실행: 섹션 3번 사용
*/

-- 예시 3: NPC 퇴장 (이벤트 종료)
/*
-- Parameters:
--   :relation_id = 'relation-uuid-123'
--   :current_turn = 42

-- 쿼리 실행: 섹션 4번 사용
-- 결과: active = false, meta.deactivated_turn = 42
*/

-- 예시 4: 특정 player의 모든 관계 조회
/*
SELECT * FROM cypher('state_db_actor_logic', $$
  MATCH (p:player {id: 'player-uuid'})-[r:RELATION]->(target)
  WHERE r.active = true
  RETURN r.relation_type, r.affinity, target.name
$$) AS (relation_type agtype, affinity agtype, target_name agtype);
*/

-- 예시 5: 세션 종료 시 모든 관계 삭제
/*
-- Parameters:
--   :session_id = 'session-uuid-123'

-- 쿼리 실행: 섹션 6번 사용
*/
