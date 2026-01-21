-- item_sync.sql
-- Rule Engine → state_DB item 동기화
-- 현재 활성 세션(session_id)을 받아서 session에 종속된 item 생성

INSERT INTO item (
    rule_item_id,
    session_id,
    name,
    description,
    item_type,
    meta
)
SELECT
    i.item_id,
    :session_id,  -- 현재 플레이 세션 UUID, 바인딩 필요
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
