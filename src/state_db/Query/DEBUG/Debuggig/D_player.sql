-- 세션당 플레이어 존재 여부 및 업데이트 시간 확인
SELECT session_id, player_id, name, updated_at
FROM player
WHERE session_id = :session_id;
