MATCH (e:Enemy {enemy_id: $enemy_id, session_id: $session_id})
SET e.is_defeated = true, e.active = false
