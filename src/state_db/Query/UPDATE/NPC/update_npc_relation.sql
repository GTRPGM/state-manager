-- [용도] NPC 간의 관계(Relation) 엣지 정보 추가/수정
UPDATE npc
SET relations = :new_relations_json
WHERE session_id = :session_id AND npc_id = :npc_id;
