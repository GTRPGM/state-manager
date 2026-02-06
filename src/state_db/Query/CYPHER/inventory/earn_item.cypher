MATCH (p:Player {id: $player_id, session_id: $session_id})
MATCH (inv:Inventory {id: $inventory_id, session_id: $session_id})
MATCH (i:Item {id: $item_uuid, session_id: $session_id})
MERGE (inv)-[c:CONTAINS]->(i)
SET c.quantity = coalesce(c.quantity, 0) + $delta_qty, c.active = true
RETURN {quantity: c.quantity}
