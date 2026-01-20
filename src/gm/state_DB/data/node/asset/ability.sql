-- Ability를 시나리오와 세션 기준으로 state DB에 넣는 템플릿
-- rule_engine에서 제공한 능력치 데이터를 불러와 session에 매핑

INSERT INTO entity (id, name, description, entity_type, state, relations, tags, created_at, updated_at)
SELECT
    gen_random_uuid(),          -- 고유 ID 생성
    a.name,                     -- ability 이름
    a.description,              -- ability 설명
    'ability',                  -- entity_type
    a.state,                    -- 능력 상태값 (JSON)
    a.relations,                -- 능력과 관련된 관계 정보 (JSON)
    a.tags,                     -- ability 태그
    NOW(),
    NOW()
FROM rule_engine_abilities a
JOIN scenario_ability_mapping sam
    ON a.ability_id = sam.ability_id
WHERE sam.scenario_id = '<현재 세션 시나리오 ID>';
