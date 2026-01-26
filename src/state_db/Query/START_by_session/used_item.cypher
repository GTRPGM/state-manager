MATCH
  (s:session),
  (p:player { id: $player_id, session_id: s.id }),
  (i:inventory { session_id: s.id }),
  (it:item { id: $item_id, session_id: s.id })
CREATE
  (i)-[:USED_ITEM {
    id: gen_random_uuid(),
    session_id: s.id,
    rule_id: $rule_id,
    created_at: now(),
    success: true
  }]->(it);
