-- npc.sql
-- Entity schema 기반 NPC Node 정의
-- 시나리오에서 생성되며 시나리오에 종속
-- 세션 시작 시 시나리오와 함께 생성

-- 1. 테이블 생성
CREATE TABLE IF NOT EXISTS npc (
    -- 엔티티 필수
    npc_id UUID NOT NULL UNIQUE,
    entity_type VARCHAR(50) NOT NULL DEFAULT 'npc',
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',

    -- session/시나리오 참조
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,
    scenario_id UUID NOT NULL,
    scenario_npc_id UUID NOT NULL,

    -- meta 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- 확장 요소
    state JSONB NOT NULL DEFAULT '{
        "numeric": {
            "HP": 100,
            "MP": 50,
            "STR": null,
            "DEX": null,
            "INT": null,
            "LUX": null,
            "SAN": 10
        },
        "boolean": {}
    }'::jsonb,

    -- RELATION 엣지 ID 저장
    relations JSONB DEFAULT '[]'::jsonb,

    -- 복합 고유 제약 (session 내에서 npc_id 고유)
    CONSTRAINT pk_npc PRIMARY KEY (npc_id, session_id)
);

-- 2. updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_npc_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_npc_updated_at
BEFORE UPDATE ON npc
FOR EACH ROW
EXECUTE FUNCTION update_npc_updated_at();

-- 3. created_at을 session.started_at과 동기화
CREATE OR REPLACE FUNCTION sync_npc_created_at()
RETURNS TRIGGER AS $$
BEGIN
    SELECT started_at INTO NEW.created_at
    FROM session
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_npc_sync_created_at
BEFORE INSERT ON npc
FOR EACH ROW
EXECUTE FUNCTION sync_npc_created_at();

-- 4. DML 예시
INSERT INTO npc (
    npc_id,
    session_id,
    scenario_id,
    scenario_npc_id,
    name,
    description,
    tags,
    state
) VALUES (
    :npc_id,           -- 시나리오에서 전달
    :session_id,       -- 현재 세션
    :scenario_id,      -- 시나리오 UUID
    :scenario_npc_id,  -- 시나리오 내 NPC ID
    :name,
    :description,
    ARRAY['npc'],
    jsonb_build_object(
        'numeric', jsonb_build_object(
            'HP', :HP,
            'MP', :MP,
            'STR', :STR,
            'DEX', :DEX,
            'INT', :INT,
            'LUX', :LUX,
            'SAN', :SAN
        ),
        'boolean', '{}'::jsonb
    )
);
