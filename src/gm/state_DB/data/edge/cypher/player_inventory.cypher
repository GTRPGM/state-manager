MATCH
  (s:session),
  (p:player { session_id: s.id }),
  (i:inventory { session_id: s.id })
MERGE
  (p)-[:PLAYER_INVENTORY {
    id: gen_random_uuid(),
    session_id: s.id,
    active: true,
    created_at: s.started_at
  }]->(i);
