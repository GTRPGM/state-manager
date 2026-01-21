-- item.sql
-- Rule Engine 기반 Item Node 정의
-- state_DB는 item의 식별자와 메타 정보만 관리

CREATE TABLE IF NOT EXISTS item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Rule Engine의 item 고유 ID
    rule_item_id UUID NOT NULL UNIQUE,

    entity_type VARCHAR(50) NOT NULL DEFAULT 'item',

    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',

    -- 아이템 분류 (소모품, 장비, 퀘스트 아이템 등)
    item_type VARCHAR(50) DEFAULT 'misc',

    -- Rule 메타 정보 (내구도 규칙, 스택 가능 여부, 버전 등)
    meta JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
