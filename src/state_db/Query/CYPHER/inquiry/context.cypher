MATCH (p:Player {id: $player_id, session_id: $session_id})
OPTIONAL MATCH (p)-[h:HAS_INVENTORY]->(inv:Inventory)-[c:CONTAINS]->(i:Item)
WHERE (h.active = true AND c.active = true) OR $include_inactive
WITH p, i, c
OPTIONAL MATCH (p)-[r:RELATION]->(n:NPC)
WHERE r.active = true OR $include_inactive
RETURN
    i.id as item_uuid,
    i.scenario as item_scenario,
    i.rule as item_rule,
    i.name as item_name,
    c.quantity as item_quantity,
    c.active as item_active,
    n.id as npc_uuid,
    n.scenario as npc_scenario,
    n.rule as npc_rule,
    n.name as npc_name,
    r.affinity as npc_affinity,
    r.relation_type as npc_relation_type,
    r.active as npc_active;
