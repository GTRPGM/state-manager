-- --------------------------------------------------------------------
-- Detail_npc.sql
-- 특정 NPC의 스탯(HP, MP 등) 및 관계(Relations) 상세 조회
-- $1: session_id, $2: npc_id
-- --------------------------------------------------------------------

SELECT
    npc_id,
    name,
    description,
    state,
    tags,
    created_at
FROM npc
WHERE session_id = $1 AND npc_id = $2;
