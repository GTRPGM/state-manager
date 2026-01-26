-- player_inventory.sql
-- 최신 세션의 모든 player에게 inventory를 자동으로 연결

-- 1️⃣ 각 player에 대해 inventory 생성 (없으면)
INSERT INTO inventory (session_id, owner_entity_type, owner_entity_id)
SELECT
    p.session_id,
    'player',
    p.id
FROM player p
WHERE p.session_id = (SELECT session_id FROM session ORDER BY started_at DESC LIMIT 1)
AND NOT EXISTS (
    SELECT 1 FROM inventory i
    WHERE i.session_id = p.session_id
    AND i.owner_entity_id = p.id
)
ON CONFLICT DO NOTHING;

-- 2️⃣ PLAYER_INVENTORY 엣지 생성
SELECT * FROM cypher('state_db', format($$
    MATCH (s:session)
    WHERE s.id = %L
    MATCH (p:player { session_id: s.id })
    MATCH (i:inventory { session_id: s.id })
    WHERE i.owner_entity_id = p.id
    AND NOT EXISTS {
        MATCH (p)-[:PLAYER_INVENTORY]->(i)
    }
    CREATE (p)-[:PLAYER_INVENTORY {
        player_inventory_id: gen_random_uuid(),
        session_id: s.id,
        active: true,
        created_at: now()
    }]->(i)
$$, (SELECT session_id FROM session ORDER BY started_at DESC LIMIT 1))) AS (v agtype);
