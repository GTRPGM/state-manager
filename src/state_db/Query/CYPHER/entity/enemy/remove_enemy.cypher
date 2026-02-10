MATCH (e:Enemy {id: $enemy_id, session_id: $session_id})
DETACH DELETE e
