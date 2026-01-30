-- [용도] 특정 아이템과 관련된 획득/소비 이력을 Turn 테이블에서 추출
-- [설명] state_changes 내에 아이템 관련 키가 포함된 기록 검색
SELECT 
    t.turn_number, 
    t.phase_at_turn, 
    t.state_changes, 
    t.created_at
FROM turn t
WHERE t.session_id = $1
  AND $2 = ANY(t.related_entities)
ORDER BY t.turn_number DESC;