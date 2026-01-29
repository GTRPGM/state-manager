-- [용도] 특정 NPC가 연관된 모든 턴 이력(사건) 조회
-- [설명] turn 테이블의 related_entities UUID 배열 내에 npc_id가 포함된 경우 검색
SELECT t.turn_number, t.phase_at_turn, t.turn_type, t.state_changes, t.created_at
FROM turn t
WHERE t.session_id = :session_id 
  AND :npc_id = ANY(t.related_entities)
ORDER BY t.turn_number DESC;