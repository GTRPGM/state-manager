// update_sequence.cypher
MATCH (s:Session {id: $session_id})
SET s.current_sequence_id = $next_sequence_id,
    s.updated_at = timestamp()
RETURN {session_id: s.id, current_sequence_id: s.current_sequence_id}
