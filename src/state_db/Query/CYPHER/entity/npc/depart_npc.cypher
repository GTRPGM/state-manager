// depart_npc.cypher
// NPC 퇴장 처리 - 그래프 노드 비활성화
MATCH (n:NPC {id: $npc_id, session_id: $session_id})
SET n.is_departed = true, n.active = false
RETURN {npc_id: n.id, name: n.name, is_departed: n.is_departed}
