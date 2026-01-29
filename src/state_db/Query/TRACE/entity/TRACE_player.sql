SELECT turn_number, state_changes 
FROM turn 
WHERE session_id = :session_id 
  AND state_changes @> jsonb_build_object('entity_type', 'player')
ORDER BY turn_number ASC;