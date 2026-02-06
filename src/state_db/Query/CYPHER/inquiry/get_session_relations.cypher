MATCH (a)-[r]->(b)
WHERE a.session_id = $session_id
  AND b.session_id = $session_id
RETURN {
    from_id: a.id,
    from_name: a.name,
    to_id: b.id,
    to_name: b.name,
    relation_type: coalesce(r.relation_type, type(r)),
    affinity: r.affinity,
    quantity: r.quantity,
    active: coalesce(r.active, true),
    activated_turn: coalesce(r.activated_turn, 0),
    deactivated_turn: r.deactivated_turn
}
