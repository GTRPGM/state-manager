MATCH (p:Player {id: $player_id, session_id: $session_id})
      -[:HAS_INVENTORY {active: true}]->(inv:Inventory)
      -[c:CONTAINS {active: true}]->(i:Item)
RETURN {
    item_id: i.id,
    quantity: c.quantity
}
