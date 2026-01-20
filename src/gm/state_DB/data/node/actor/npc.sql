-- 예시: scenario_id에 따라 NPC 불러오기
INSERT INTO entity (id, name, description, entity_type, state, relations, tags, created_at, updated_at)
SELECT
    gen_random_uuid(),
    n.name,
    n.description,
    'npc',
    n.state,
    n.relations,
    n.tags,
    NOW(),
    NOW()
FROM scenario_npc_mapping sn
JOIN npc_reference n ON sn.npc_id = n.npc_id
WHERE sn.scenario_id = '<현재 세션 시나리오 ID>';
