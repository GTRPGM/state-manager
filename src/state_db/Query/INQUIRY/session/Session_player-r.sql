-- --------------------------------------------------------------------
-- 8-1. Session + Player 통합 조회
-- 용도: 게임 전체 상태 조회
-- API: GET /state/session/{session_id}/full
-- --------------------------------------------------------------------

SELECT
    -- Session 정보
    s.session_id,
    s.scenario_id,
    s.current_act,
    s.current_sequence,
    s.current_phase,
    s.current_turn,
    s.location,
    s.status,

    -- Player 정보
    p.player_id,
    p.name AS player_name,
    p.hp,
    p.max_hp,
    p.gold,

    -- 통계
    (SELECT COUNT(*) FROM player_inventory pi WHERE pi.player_id = p.player_id) AS item_count,
    (SELECT COUNT(*) FROM player_npc_relations pnr WHERE pnr.player_id = p.player_id) AS npc_relation_count
FROM session s
LEFT JOIN player p ON s.session_id = p.session_id
WHERE s.session_id = $1;
