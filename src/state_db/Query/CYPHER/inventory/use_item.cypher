MATCH (p:Player {id: $player_id, session_id: $session_id})-[h:HAS_INVENTORY {active: true}]->(inv:Inventory {id: $inventory_id, session_id: $session_id})-[c:CONTAINS {active: true}]->(i:Item {id: $item_uuid, session_id: $session_id, scenario: $scenario, rule: $rule})
SET c.quantity = c.quantity - $use_qty
WITH c
CASE
    WHEN c.quantity <= 0 THEN
        SET c.active = false,
            c.deactivated_turn = $turn,
            c.quantity = 0
END
RETURN c.quantity as quantity, c.active as active;
