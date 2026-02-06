// get_session_enemies.cypher
// 그래프에서 Enemy ID만 조회 (상태 데이터는 SQL에서 결합)
MATCH (e:Enemy {session_id: $session_id})
WHERE ($active_only = false OR e.active = true)
RETURN {id: e.id}
