// update_enemy_hp.cypher
// Enemy HP 변경 - 그래프 노드 속성 업데이트 (미사용: SQL 트리거 경유)
MATCH (e:Enemy {id: $enemy_id, session_id: $session_id})
SET e.hp = coalesce(e.hp, 0) + $hp_change
RETURN {id: e.id, current_hp: e.hp}
