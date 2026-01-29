-- [용도] 특정 NPC의 스탯(HP, MP 등) 및 관계(Relations) 상세 조회
SELECT *
FROM npc
WHERE session_id = :session_id AND npc_id = :npc_id;