-- [용도] 현재 세션에 존재하는 모든 NPC의 기본 정보와 상태 조회
SELECT npc_id, name, description, state, tags
FROM npc
WHERE session_id = :session_id;
