-- ability_sync.sql
-- Rule Engine → state_db ability 동기화
-- 현재 활성 세션(session_id)을 받아서 session에 종속된 ability 생성

INSERT INTO ability (
    rule_ability_id,
    session_id,
    name,
    description,
    ability_type,
    meta
)
SELECT
    a.ability_id,
    :session_id,  -- 현재 플레이 세션 UUID, 바인딩 필요
    a.name,
    a.description,
    a.ability_type,
    jsonb_build_object(
        'rule_version', a.version,
        'source', 'rule_engine'
    )
FROM rule_engine_abilities a
ON CONFLICT (rule_ability_id) DO NOTHING;
