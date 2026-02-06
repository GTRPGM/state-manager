MATCH (cause {session_id: $session_id}), (effect {session_id: $session_id})
WHERE (cause.id = $cause_entity_id OR cause.tid = $cause_entity_id)
  AND (effect.id = $effect_entity_id OR effect.tid = $effect_entity_id)
MERGE (cause)-[r:RELATION {relation_type: $relation_type}]->(effect)
SET
    r.active = true,
    r.activated_turn = coalesce(r.activated_turn, $turn),
    r.deactivated_turn = null,
    r.affinity = coalesce($affinity_score, r.affinity),
    r.quantity = coalesce($quantity, r.quantity)
RETURN {
    cause_entity_id: coalesce(cause.id, cause.tid),
    effect_entity_id: coalesce(effect.id, effect.tid),
    relation_type: r.relation_type,
    affinity_score: r.affinity,
    quantity: r.quantity,
    active: r.active
}
