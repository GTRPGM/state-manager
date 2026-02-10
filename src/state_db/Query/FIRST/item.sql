CREATE TABLE IF NOT EXISTS item (
    -- Rule Engine의 item 고유 ID
    item_id UUID PRIMARY KEY,

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
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_item_session_id ON item(session_id);
CREATE INDEX IF NOT EXISTS idx_item_type ON item(item_type);

-- 주석
COMMENT ON TABLE item IS 'RuleEngine에서 관리하는 아이템 정의 테이블';
COMMENT ON COLUMN item.item_id IS 'RuleEngine 생성 아이템 고유 ID';
COMMENT ON COLUMN item.session_id IS '아이템이 속한 세션 ID';

-- 2. created_at을 session.started_at과 동기화하는 트리거
CREATE OR REPLACE FUNCTION initialize_items()
RETURNS TRIGGER AS $$
BEGIN
    -- 시나리오에 정의된 아이템들을 session에 로드
    -- 실제 구현 시 scenario_items 테이블에서 가져와야 함

    INSERT INTO item (
        item_id,
        session_id,
        name,
        description,
        item_type,
        created_at
    )
    VALUES
    (
        gen_random_uuid(),
        NEW.session_id,
        'Health Potion',
        'Restores 50 HP',
        'consumable',
        NEW.started_at
    ),
    (
        gen_random_uuid(),
        NEW.session_id,
        'Rusty Sword',
        'An old sword',
        'equipment',
        NEW.started_at
    );

    RAISE NOTICE '[Item] Initial items loaded for session %', NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_05_initialize_items ON session;
CREATE TRIGGER trigger_05_initialize_items
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_items();
