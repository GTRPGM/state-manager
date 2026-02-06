MATCH (i:Item {session_id: $session_id})
RETURN i.id as id
