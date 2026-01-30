-- ====================================================================
-- B_item.sql
-- 아이템 엔티티 테이블 구조 (Base)
-- ====================================================================


CREATE TABLE IF NOT EXISTS item (
    -- Rule Engine의 item 고유 ID (int 형태로 전달받음)
    item_id INT NOT NULL,

    -- 엔티티 유형
    entity_type VARCHAR(10) NOT NULL DEFAULT 'item',

    -- 세션 참조
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,

    -- 복합 Primary Key (같은 item_id가 여러 세션에 존재 가능)
    PRIMARY KEY (item_id, session_id),
    scenario_id UUID NOT NULL,
    scenario_item_id VARCHAR(100) NOT NULL, -- 직관적 식별자 (예: 'ITEM_POTION_01')

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
CREATE INDEX IF NOT EXISTS idx_item_scenario_id ON item(scenario_id);
CREATE INDEX IF NOT EXISTS idx_item_scenario_item_id ON item(scenario_item_id);
CREATE INDEX IF NOT EXISTS idx_item_type ON item(item_type);

-- 주석
COMMENT ON TABLE item IS 'RuleEngine에서 관리하는 아이템 정의 테이블';
