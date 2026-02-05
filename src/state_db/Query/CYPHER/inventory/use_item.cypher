MATCH (p:Player {id: $player_id, session_id: $session_id})
      -[:HAS_INVENTORY {active: true}]->(inv:Inventory {id: $inventory_id, session_id: $session_id})
      -[c:CONTAINS {active: true}]->(i:Item {id: $item_uuid, session_id: $session_id, scenario: $scenario, rule: $rule})
SET c.quantity = c.quantity - $use_qty
WITH c, CASE WHEN c.quantity <= 0 THEN true ELSE false END as should_deactivate
SET c.active = CASE WHEN should_deactivate THEN false ELSE c.active END,
    c.deactivated_turn = CASE WHEN should_deactivate THEN $turn ELSE c.deactivated_turn END,
    c.quantity = CASE WHEN c.quantity < 0 THEN 0 ELSE c.quantity END
RETURN c.quantity as quantity, c.active as active
