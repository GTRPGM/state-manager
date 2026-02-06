MATCH (e:Enemy {session_id: $session_id})
WHERE ($active_only = false OR e.active = true)
RETURN e.id as id
