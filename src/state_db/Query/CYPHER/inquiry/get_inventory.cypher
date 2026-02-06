MATCH (p:Player {id: $player_id, session_id: $session_id})
      -[:HAS_INVENTORY {active: true}]->(inv:Inventory)
      -[c:CONTAINS {active: true}]->(i:Item)
RETURN {
    player_id: p.id,
    item_id: i.id,
    rule_id: i.rule,
    item_name: i.name,
    description: i.description,
    quantity: c.quantity,
    active: c.active,
    activated_turn: c.activated_turn,
    deactivated_turn: c.deactivated_turn
}
