// return_npc.cypher
// NPC 복귀 처리 - 그래프 노드 재활성화
MATCH (n:NPC {id: $npc_id, session_id: $session_id})
SET n.is_departed = false, n.active = true
RETURN {npc_id: n.id, name: n.name, is_departed: n.is_departed}
