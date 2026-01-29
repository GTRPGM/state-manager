-- 특정 적 제거 (사망 처리 등)
DELETE FROM enemy 
WHERE enemy_id = '{enemy_uuid}' AND session_id = '{session_uuid}';