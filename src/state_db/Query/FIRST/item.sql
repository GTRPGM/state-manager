CREATE TABLE IF NOT EXISTS item (
    -- Rule Engine의 item 고유 ID
    item_id UUID NOT NULL UNIQUE,

    -- 엔티티 유형
    entity_type VARCHAR(10) NOT NULL DEFAULT 'item',

    -- 세션 참조 | 세션 시작하면 생성되서 받아오면 됨
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,

    name VARCHAR(20) NOT NULL,
    description TEXT DEFAULT '',

    -- 아이템 분류 (소모품, 장비, 퀘스트 아이템 등)
    item_type VARCHAR(20) DEFAULT 'misc',

    -- Rule 메타 정보 (내구도 규칙, 스택 가능 여부, 버전 등)
    meta JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (item_id, session_id)
);

CREATE OR REPLACE FUNCTION sync_item_created_at()
RETURNS TRIGGER AS $$
BEGIN
    SELECT started_at INTO NEW.created_at
    FROM session
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_item_sync_created_at ON item;
CREATE TRIGGER trg_item_sync_created_at
BEFORE INSERT ON item
FOR EACH ROW
EXECUTE FUNCTION sync_item_created_at();
