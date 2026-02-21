MATCH (c {session_id: $session_id})
WHERE (c.id = $cause_entity_id OR c.tid = $cause_entity_id)
WITH c
ORDER BY CASE WHEN c.tid = $cause_entity_id THEN 0 ELSE 1 END, id(c)
LIMIT 1
MATCH (e {session_id: $session_id})
WHERE (e.id = $effect_entity_id OR e.tid = $effect_entity_id)
WITH c AS cause, e
ORDER BY CASE WHEN e.tid = $effect_entity_id THEN 0 ELSE 1 END, id(e)
LIMIT 1
MERGE (cause)-[r:RELATION {relation_type: $relation_type}]->(e)
SET
    r.active = true,
    r.activated_turn = coalesce(r.activated_turn, $turn),
    r.deactivated_turn = null,
    r.affinity = coalesce($affinity_score, r.affinity),
    r.quantity = coalesce($quantity, r.quantity)
RETURN {
    cause_entity_id: coalesce(cause.id, cause.tid),
    effect_entity_id: coalesce(e.id, e.tid),
    relation_type: r.relation_type,
    affinity_score: r.affinity,
    quantity: r.quantity,
    active: r.active
}
