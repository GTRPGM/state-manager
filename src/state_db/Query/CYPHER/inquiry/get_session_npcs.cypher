MATCH (n:NPC {session_id: $session_id})
WHERE ($active_only = false OR n.active = true)
RETURN n.id as id
