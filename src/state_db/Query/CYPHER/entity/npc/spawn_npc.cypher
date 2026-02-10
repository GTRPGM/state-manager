// spawn_npc.cypher
// NPC 그래프 노드 생성 (Minimalist: id, name, active, tid, scenario_id)
// 트리거(sync_entity_to_graph)와 MERGE로 일관성 유지
MERGE (n:NPC {id: $npc_id, session_id: $session_id})
SET n.name = $name, n.active = true, n.tid = $scenario_npc_id, n.scenario_id = $scenario_id
RETURN {id: n.id, name: n.name}
