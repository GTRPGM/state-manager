// defeat_enemy.cypher
// Enemy 처치 처리 - 그래프 노드 비활성화
MATCH (e:Enemy {id: $enemy_id, session_id: $session_id})
SET e.is_defeated = true, e.active = false
RETURN {id: e.id, name: e.name, is_defeated: e.is_defeated}
