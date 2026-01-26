MATCH
  (s:session),
  (p:player { id: $player_id, session_id: s.id }),
  (i:inventory { session_id: s.id }),
  (it:item { id: $item_id, session_id: s.id })
MERGE
  (i)-[r:INVENTORY_ITEM]->(it)
SET
  r.session_id = s.id,
  r.active = true,
  r.updated_at = now();
