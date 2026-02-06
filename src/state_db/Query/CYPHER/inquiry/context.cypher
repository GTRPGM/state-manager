MATCH (p:Player {id: $player_id, session_id: $session_id})

// 1. Inventory Items
OPTIONAL MATCH (p)-[h:HAS_INVENTORY]->(inv:Inventory)-[c:CONTAINS]->(i:Item)
WHERE (h.active = true AND c.active = true) OR $include_inactive
WITH p, i, c
ORDER BY i.name
WITH p, collect(CASE WHEN i.id IS NOT NULL THEN {
    item_uuid: i.id,
    item_scenario: i.scenario,
    item_rule: i.rule,
    item_name: i.name,
    item_quantity: c.quantity,
    item_active: c.active
} END) as items

// 2. NPC Relations
OPTIONAL MATCH (p)-[r:RELATION]->(n:NPC)
WHERE r.active = true OR $include_inactive
WITH p, items, n, r
ORDER BY n.name
WITH p, items, collect(CASE WHEN n.id IS NOT NULL THEN {
    npc_uuid: n.id,
    npc_scenario: n.scenario,
    npc_rule: n.rule,
    npc_name: n.name,
    npc_affinity: r.affinity,
    npc_relation_type: r.relation_type,
    npc_active: r.active
} END) as npcs

// 3. Enemies (Active)
OPTIONAL MATCH (e:Enemy {session_id: $session_id})
WHERE e.active = true OR $include_inactive
WITH p, items, npcs, e
ORDER BY e.name
WITH p, items, npcs, collect(CASE WHEN e.id IS NOT NULL THEN {
    enemy_uuid: e.id,
    enemy_scenario: e.scenario,
    enemy_rule: e.rule,
    enemy_name: e.name,
    enemy_hp: e.hp,
    enemy_active: e.active
} END) as enemies

RETURN {
    items: items,
    npcs: npcs,
    enemies: enemies
}
