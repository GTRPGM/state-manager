MATCH (n:NPC {npc_id: $npc_id, session_id: $session_id})
SET n.is_departed = false
RETURN {
    npc_id: n.npc_id,
    name: n.name,
    is_departed: n.is_departed
}
