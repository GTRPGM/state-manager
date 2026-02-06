MATCH (i:Item {session_id: $session_id})
RETURN {
    item_id: coalesce(i.item_id, i.id),
    scenario_item_id: coalesce(i.scenario_item_id, i.scenario),
    rule_id: coalesce(i.rule_id, i.rule),
    name: i.name,
    description: i.description,
    item_type: i.item_type,
    meta: i.meta
}
