MATCH (p:Player {id: $player_id, session_id: $session_id})
MATCH (inv:Inventory {id: $inventory_id, session_id: $session_id})
MATCH (i:Item {id: $item_uuid, session_id: $session_id, scenario: $scenario, rule: $rule})
MERGE (p)-[h:HAS_INVENTORY]->(inv)
SET h.active = true,
    h.activated_turn = coalesce(h.activated_turn, $turn)
MERGE (inv)-[c:CONTAINS]->(i)
ON CREATE SET
    c.quantity = $delta_qty,
    c.active = true,
    c.activated_turn = $turn
ON MATCH SET
    c.quantity = c.quantity + $delta_qty,
    c.active = true,
    c.deactivated_turn = null
RETURN c.quantity as quantity;
