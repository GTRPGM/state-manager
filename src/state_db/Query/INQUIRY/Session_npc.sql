-- --------------------------------------------------------------------
-- Session_npc.sql
-- 세션의 NPC 목록 조회
-- 용도: 현재 세션에 존재하는 모든 NPC 확인
-- API: GET /state/session/{session_id}/npcs
-- --------------------------------------------------------------------

SELECT
    npc_id,
    name,
    description,
    (state->'numeric'->>'HP')::int AS hp,
    tags
FROM npc
WHERE session_id = $1
ORDER BY created_at ASC;
