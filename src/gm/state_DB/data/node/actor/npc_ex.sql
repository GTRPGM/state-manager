-- npc.sql DML 예시
-- 시나리오 작성자가 NPC 정보를 입력하고 session에 생성할 때 사용

INSERT INTO npc (
    name,                -- NPC 이름: 작성자가 입력
    description,         -- NPC 설명: 작성자가 입력
    session_id,          -- 현재 플레이 세션 UUID
    scenario_id,         -- 참조 시나리오 UUID
    scenario_npc_id,     -- 시나리오 내 NPC 고유 ID
    tags,                -- 분류/검색용 태그 배열
    state,               -- 초기 상태: HP, 위치, 버프 등
    relations            -- 초기 관계: player, item, ability 등과의 edge
) VALUES (
    'Goblin',                        -- name
    '초기 전투용 고블린',             -- description
    '<session_uuid>',                 -- session_id: 플레이 중인 세션
    '<scenario_uuid>',                -- scenario_id: 시나리오 참조
    '<scenario_npc_uuid>',            -- scenario_npc_id: 시나리오 내 NPC ID
    ARRAY['enemy', 'melee'],          -- tags
    '{
        "numeric": {
            "HP": 50,
            "MP": 0,
            "STR": 8,
            "DEX": 6,
            "INT": 3,
            "SAN": 10
        },
        "boolean": {
            "poisoned": false,
            "stunned": false
        }
    }'::jsonb,
    '{}'::jsonb                       -- relations 초기값은 빈 객체
);
