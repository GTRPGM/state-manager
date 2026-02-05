MATCH (p:Player {id: $player_id, session_id: $session_id})
      -[:HAS_INVENTORY {active: true}]->(inv:Inventory)
      -[c:CONTAINS {active: true}]->(i:Item)
RETURN p.id as player_id,
       i.id as item_id,
       i.rule as rule_id,
       i.name as item_name,
       i.description as description,
       c.quantity as quantity,
       c.active as active,
       c.activated_turn as activated_turn,
       c.deactivated_turn as deactivated_turn
