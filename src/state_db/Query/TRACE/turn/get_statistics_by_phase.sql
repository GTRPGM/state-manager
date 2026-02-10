-- Phase별 진행된 턴 수 집계
SELECT phase_at_turn, COUNT(*) AS turn_count
FROM turn
WHERE session_id = :session_id
GROUP BY phase_at_turn;
