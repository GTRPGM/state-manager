-- item_Querry.sql
-- Rule Engine → state_db item 동기화
-- 현재 활성 세션(session_id)을 받아서 session에 종속된 item 생성

INSERT INTO item (
    item_id,
    session_id,
    name,
    description,
    item_type,
    meta,
    created_at
)
SELECT
    it.item_id,
    :session_id,  -- 현재 플레이 세션 UUID, 바인딩 필요
    it.name,
    it.description,
    it.item_type,
    jsonb_build_object(
        'rule_version', it.version,
        'stackable', it.stackable,
        'max_stack', it.max_stack,
        'source', 'rule_engine'
    ),
    s.started_at
FROM items it
JOIN session s ON s.session_id = :session_id
ON CONFLICT (item_id) DO NOTHING;
