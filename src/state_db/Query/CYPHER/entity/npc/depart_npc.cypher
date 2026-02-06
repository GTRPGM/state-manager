MATCH (n:NPC {npc_id: $npc_id, session_id: $session_id})
SET n.is_departed = true
RETURN n.npc_id as npc_id, n.name as name, n.is_departed as is_departed
