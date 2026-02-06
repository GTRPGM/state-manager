MATCH (n:NPC {session_id: $session_id})
WHERE ($active_only = false OR n.is_departed = false)
RETURN {
    npc_id: coalesce(n.npc_id, n.id),
    scenario_npc_id: coalesce(n.scenario_npc_id, n.scenario),
    rule_id: coalesce(n.rule_id, n.rule),
    name: n.name,
    description: n.description,
    current_hp: coalesce(n.current_hp, n.hp),
    tags: n.tags,
    state: n.state,
    assigned_sequence_id: coalesce(n.assigned_sequence_id, n.sequence_id),
    assigned_location: coalesce(n.assigned_location, n.location),
    is_departed: coalesce(n.is_departed, false)
}
