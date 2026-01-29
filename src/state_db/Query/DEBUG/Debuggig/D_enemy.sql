-- 1. 복제 무결성 검사: Master Session(0번)과 현재 세션의 데이터 개수 비교
SELECT 
    (SELECT count(*) FROM enemy WHERE session_id = '00000000-0000-0000-0000-000000000000') AS master_cnt,
    (SELECT count(*) FROM enemy WHERE session_id = :session_id) AS session_cnt;

-- 2. 턴-상태 불일치 검사: enemy_id가 존재하는데 turn 기록이 없는 경우 탐지
SELECT e.enemy_id, e.name
FROM enemy e
LEFT JOIN turn t ON e.session_id = t.session_id 
  AND t.state_changes @> jsonb_build_object('entity_id', e.enemy_id)
WHERE e.session_id = :session_id AND t.turn_id IS NULL;