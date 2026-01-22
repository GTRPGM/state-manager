-- item.sql
-- Rule Engine 기반 Item Node 정의
-- state_DB는 item의 식별자와 meta 정보만 관리
-- 모든 item은 session_id에 종속

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
    created_at TIMESTAMP NOT NULL
        DEFAULT (SELECT started_at FROM session WHERE session_id = session_id)
);
