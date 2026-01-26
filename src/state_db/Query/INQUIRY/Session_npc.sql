-- --------------------------------------------------------------------
-- Session_npc.sql
-- 세션의 NPC 목록 조회
-- 용도: 현재 세션에 존재하는 모든 NPC 확인
-- API: GET /state/session/{session_id}/npcs
-- --------------------------------------------------------------------

SELECT
    npc_id,
    entity_type,
    name,
    description,
    state,
    tags,
    created_at,
    updated_at
FROM npc
WHERE session_id = $1
ORDER BY created_at ASC;

-- 결과 예:
-- npc_id   | entity_type | name         | description           | state           | tags
-- ---------|-------------|--------------|----------------------|-----------------|-------------
-- uuid-456 | npc         | Merchant Tom | A friendly merchant  | {"hp": 100, ...}| ["merchant"]
-- uuid-789 | npc         | Guard John   | Town guard           | {"hp": 150, ...}| ["guard"]
