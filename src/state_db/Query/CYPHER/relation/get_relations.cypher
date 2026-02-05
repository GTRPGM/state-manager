MATCH (p:Player {id: $player_id, session_id: $session_id})-[r:RELATION]->(n:NPC)
WHERE r.active = true
RETURN n.npc_id as npc_id,
       n.name as npc_name,
       r.affinity as affinity_score,
       r.active as active,
       r.activated_turn as activated_turn,
       r.deactivated_turn as deactivated_turn,
       r.relation_type as relation_type
