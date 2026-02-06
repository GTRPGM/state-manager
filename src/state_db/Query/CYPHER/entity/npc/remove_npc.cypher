MATCH (n:NPC {id: $npc_id, session_id: $session_id})
DETACH DELETE n
