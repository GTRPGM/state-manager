-- 특정 적과 관련된 상태 변화 이력 조회 (turn_id 기반)
SELECT turn_number, state_changes 
FROM turn 
WHERE session_id = $1
  AND state_changes @> jsonb_build_object('entity_id', $2)
ORDER BY turn_number ASC;