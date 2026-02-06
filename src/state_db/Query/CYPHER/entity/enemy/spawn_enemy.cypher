// spawn_enemy.cypher
// Enemy 그래프 노드 생성 (Minimalist: id, name, active, tid, scenario_id)
// 트리거(sync_entity_to_graph)와 MERGE로 일관성 유지
MERGE (e:Enemy {id: $enemy_id, session_id: $session_id})
SET e.name = $name, e.active = true, e.tid = $scenario_enemy_id, e.scenario_id = $scenario_id
RETURN {id: e.id, name: e.name}
