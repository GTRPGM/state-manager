MATCH (p:Player {id: $player_id, session_id: $session_id})-[r:RELATION]->(n:NPC)
WHERE r.active = true
RETURN {
    npc_id: coalesce(n.id, n.npc_id),
    npc_name: n.name,
    affinity_score: r.affinity,
    active: r.active,
    activated_turn: r.activated_turn,
    deactivated_turn: r.deactivated_turn,
    relation_type: r.relation_type
}
