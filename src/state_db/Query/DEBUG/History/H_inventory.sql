-- [용도] 특정 인벤토리(가방)와 관련된 모든 턴 이력 조회
-- [설명] turn 테이블의 related_entities에 inventory_id가 포함된 기록 추출
SELECT 
    t.turn_number, 
    t.turn_type, 
    t.state_changes, 
    t.created_at
FROM turn t
WHERE t.session_id = $1
  AND $2 = ANY(t.related_entities)
ORDER BY t.turn_number DESC;
