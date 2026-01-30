-- Session_enemy.sql
-- 현재 세션의 '위치'와 '시퀀스'에 맞는 적들만 조회

SELECT
    e.enemy_id AS enemy_instance_id,
    e.scenario_enemy_id,
    e.name,
    e.description,
    e.state,
    e.is_defeated,
    e.tags,
    e.assigned_location,
    e.assigned_sequence_id
FROM enemy e
JOIN session s ON e.session_id = s.session_id
WHERE s.session_id = $1
  AND (
      -- 시퀀스 ID 기반 필터링
      e.assigned_sequence_id = s.current_sequence_id
      OR
      -- 장소명 기반 필터링 (동적 탐색 대응)
      e.assigned_location = s.location
  )
  AND (CASE WHEN $2 = true THEN e.is_defeated = false ELSE true END);
