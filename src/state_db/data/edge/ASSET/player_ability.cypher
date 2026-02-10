MATCH
  (s:session),
  (p:player { id: $player_id, session_id: s.id }),
  (ab:ability { session_id: s.id }),
  (it:item { id: $item_id, session_id: s.id })
MERGE
  (p)-[r:PLAYER_ABILITY]->(ab)
SET
  r.session_id = s.id,
  r.active = true,
  r.updated_at = now();
