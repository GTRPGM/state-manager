-- item.sql
-- Rule Engine 기반 Item Node 정의
-- state_DB는 item의 식별자와 meta 정보만 관리
-- 모든 item은 session_id에 종속

CREATE TABLE IF NOT EXISTS item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Rule Engine의 item 고유 ID
    rule_item_id UUID NOT NULL UNIQUE,

    -- 엔티티 유형
    entity_type VARCHAR(50) NOT NULL DEFAULT 'item',

    -- 세션 참조 (모든 Node는 session_id에 종속)
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,

    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',

    -- 아이템 분류 (소모품, 장비, 퀘스트 아이템 등)
    item_type VARCHAR(50) DEFAULT 'misc',

    -- Rule 메타 정보 (내구도 규칙, 스택 가능 여부, 버전 등)
    meta JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_item_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_item_updated_at
BEFORE UPDATE ON item
FOR EACH ROW
EXECUTE FUNCTION update_item_updated_at();
