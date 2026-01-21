-- ability_sync.sql
-- Rule Engine → state_DB ability 동기화

INSERT INTO ability (
    rule_ability_id,
    name,
    description,
    ability_type,
    meta
)
SELECT
    a.ability_id,
    a.name,
    a.description,
    a.ability_type,
    jsonb_build_object(
        'rule_version', a.version,
        'source', 'rule_engine'
    )
FROM rule_engine_abilities a
ON CONFLICT (rule_ability_id) DO NOTHING;
