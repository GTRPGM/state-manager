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
