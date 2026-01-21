-- item_sync.sql
-- Rule Engine → state_DB item 동기화

INSERT INTO item (
    rule_item_id,
    name,
    description,
    item_type,
    meta
)
SELECT
    i.item_id,
    i.name,
    i.description,
    i.item_type,
    jsonb_build_object(
        'rule_version', i.version,
        'stackable', i.stackable,
        'max_stack', i.max_stack,
        'source', 'rule_engine'
    )
FROM rule_engine_items i
ON CONFLICT (rule_item_id) DO NOTHING;
