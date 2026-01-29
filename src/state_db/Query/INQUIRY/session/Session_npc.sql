-- --------------------------------------------------------------------
-- Session_npc.sql
-- 세션의 NPC 목록 조회
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    npc_id,
    name,
    description,
    (state->'numeric'->>'HP')::int AS current_hp,
    tags,
    state
FROM npc
WHERE session_id = $1
ORDER BY name ASC;
