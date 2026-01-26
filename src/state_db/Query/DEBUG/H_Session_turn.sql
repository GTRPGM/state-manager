-- --------------------------------------------------------------------
-- 8-3. Session + Turn History 조회
-- 용도: 게임 진행 타임라인
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.current_turn,
    th.turn_number,
    th.phase_at_turn,
    th.turn_type,
    th.state_changes,
    th.created_at
FROM session s
LEFT JOIN turn_history th ON s.session_id = th.session_id
WHERE s.session_id = $1
ORDER BY th.turn_number ASC;
