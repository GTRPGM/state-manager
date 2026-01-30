-- [용도] NPC 간의 관계(Relation) 엣지 정보 추가/수정
-- $1: session_id, $2: npc_id, $3: new_relations_json
UPDATE npc
SET relations = $3::jsonb
WHERE session_id = $1::uuid AND npc_id = $2::uuid;
