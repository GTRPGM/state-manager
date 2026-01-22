MATCH
  (s:session),
  (p:player { id: $player_id, session_id: s.id }),
  (i:inventory { session_id: s.id })
CREATE
  (p)-[:PLAYER_INVENTORY {
    id: gen_random_uuid(),
    session_id: s.id,
    active: true,
    created_at: s.started_at
  }]->(i);
