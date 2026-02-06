MATCH (e:Enemy {enemy_id: $enemy_id, session_id: $session_id})
SET e.hp = coalesce(e.hp, 0) + $hp_change
RETURN {enemy_id: e.enemy_id, current_hp: e.hp}
