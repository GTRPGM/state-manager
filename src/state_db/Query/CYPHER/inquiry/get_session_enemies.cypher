MATCH (e:Enemy {session_id: $session_id})
WHERE ($active_only = false OR e.is_defeated = false)
RETURN {
    enemy_id: coalesce(e.enemy_id, e.id),
    scenario_enemy_id: coalesce(e.scenario_enemy_id, e.scenario),
    rule_id: coalesce(e.rule_id, e.rule),
    name: e.name,
    description: e.description,
    current_hp: coalesce(e.current_hp, e.hp),
    tags: e.tags,
    state: e.state,
    assigned_sequence_id: coalesce(e.assigned_sequence_id, e.sequence_id),
    assigned_location: coalesce(e.assigned_location, e.location),
    is_defeated: coalesce(e.is_defeated, false)
}
