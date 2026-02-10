MATCH (p:Player {id: $player_id, session_id: $session_id})

// 1. Inventory Items
OPTIONAL MATCH (p)-[h:HAS_INVENTORY]->(inv:Inventory)-[c:CONTAINS]->(i:Item)
WHERE (h.active = true AND c.active = true) OR $include_inactive
WITH p, i, c
ORDER BY i.name
WITH p, collect(CASE WHEN i.id IS NOT NULL THEN {
    id: i.id,
    name: i.name,
    quantity: c.quantity,
    active: c.active
} END) as items

// 2. NPC Relations
OPTIONAL MATCH (p)-[r:RELATION]->(n:NPC)
WHERE r.active = true OR $include_inactive
WITH p, items, n, r
ORDER BY n.name
WITH p, items, collect(CASE WHEN n.id IS NOT NULL THEN {
    id: n.id,
    name: n.name,
    affinity: r.affinity,
    relation_type: r.relation_type,
    active: r.active
} END) as npcs

// 3. Enemies (Active)
OPTIONAL MATCH (e:Enemy {session_id: $session_id})
WHERE e.active = true OR $include_inactive
WITH p, items, npcs, e
ORDER BY e.name
WITH p, items, npcs, collect(CASE WHEN e.id IS NOT NULL THEN {
    id: e.id,
    name: e.name,
    active: e.active
} END) as enemies

RETURN {
    items: items,
    npcs: npcs,
    enemies: enemies
}
