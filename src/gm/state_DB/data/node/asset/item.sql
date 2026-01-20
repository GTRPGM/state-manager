-- Item을 시나리오와 세션 기준으로 state DB에 넣는 템플릿
-- rule_engine에서 제공한 아이템 데이터를 기반으로 state DB에 INSERT

INSERT INTO entity (id, name, description, entity_type, state, relations, tags, created_at, updated_at)
SELECT
    gen_random_uuid(),          -- 고유 ID
    i.name,                     -- 아이템 이름
    i.description,              -- 설명
    'item',                     -- entity_type
    i.state,                    -- 아이템 상태 (ex. durability, charges)
    i.relations,                -- 아이템 관련 관계 정보
    i.tags,                     -- 태그
    NOW(),
    NOW()
FROM rule_engine_items i
JOIN scenario_item_mapping sim
    ON i.item_id = sim.item_id
WHERE sim.scenario_id = '<현재 세션 시나리오 ID>';
