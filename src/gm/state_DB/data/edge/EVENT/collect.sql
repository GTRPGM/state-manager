-- collect.sql: 아이템 획득 트리거 + 메시지 + 이벤트 삭제 + 재발생 가능

-- 1️⃣ 아이템 획득 처리 (MERGE INVENTORY_ITEM edge)
SELECT *
FROM cypher('state_db_item_logic', $$
  MATCH
    (p:player { id: $player_id, session_id: $session_id }),
    (i:inventory { session_id: $session_id }),
    (it:item { id: $item_id, session_id: $session_id })
  MERGE
    (i)-[r:INVENTORY_ITEM]->(it)
  ON CREATE SET
    r.session_id = $session_id,
    r.active = true,
    r.created_at = now()
  ON MATCH SET
    r.active = true,
    r.updated_at = now()
$$) AS (v agtype);

-- 2️⃣ 메시지 생성 (얻었다 알림)
SELECT *
FROM cypher('state_db_item_logic', $$
  MATCH
    (p:player { id: $player_id, session_id: $session_id }),
    (it:item { id: $item_id, session_id: $session_id })
  CREATE
    (p)-[:MESSAGE {
      id: gen_random_uuid(),
      content: it.name + "을(를) 얻었습니다.",
      created_at: now()
    }]->(it)
$$) AS (v agtype);

-- 3️⃣ 이벤트 처리 후 EARN_ITEM edge 삭제 (트리거 초기화)
SELECT *
FROM cypher('state_db_item_logic', $$
  MATCH (i:inventory { session_id: $session_id })-[r:EARN_ITEM]->(it:item { id: $item_id })
  DELETE r
$$) AS (v agtype);
