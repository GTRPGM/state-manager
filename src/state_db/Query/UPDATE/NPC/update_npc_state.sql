-- [용도] NPC의 HP, MP 등 JSONB 내 수치 데이터 업데이트
-- [설명] || 연산자를 사용하여 기존 state를 보존하며 특정 키만 갱신
UPDATE npc
SET state = state || :new_state_json,
    updated_at = NOW()
WHERE session_id = :session_id AND npc_id = :npc_id;