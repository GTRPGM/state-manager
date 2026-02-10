// get_session_npcs.cypher
// 그래프에서 NPC ID만 조회 (상태 데이터는 SQL에서 결합)
MATCH (n:NPC {session_id: $session_id})
WHERE ($active_only = false OR n.active = true)
RETURN {id: n.id}
