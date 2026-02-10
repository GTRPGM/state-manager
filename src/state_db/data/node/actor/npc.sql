CREATE TABLE IF NOT EXISTS npc (
    -- 엔티티 필수
    npc_id UUID PRIMARY KEY,
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
    relations JSONB DEFAULT '[]'::jsonb
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_npc_session_id ON npc(session_id);
CREATE INDEX IF NOT EXISTS idx_npc_scenario_id ON npc(scenario_id);
CREATE INDEX IF NOT EXISTS idx_npc_scenario_npc_id ON npc(scenario_npc_id);

-- 주석
COMMENT ON TABLE npc IS '시나리오에서 정의된 NPC 테이블';
COMMENT ON COLUMN npc.npc_id IS 'NPC 고유 ID (시나리오 생성)';
COMMENT ON COLUMN npc.session_id IS 'NPC가 속한 세션 ID';
COMMENT ON COLUMN npc.scenario_npc_id IS '시나리오에서의 NPC 템플릿 ID';

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
CREATE OR REPLACE FUNCTION initialize_npcs()
RETURNS TRIGGER AS $$
BEGIN
    -- 시나리오에 정의된 초기 NPC들을 생성
    -- 실제 구현 시 scenario_npcs 테이블에서 가져와야 함

    INSERT INTO npc (
        npc_id,
        session_id,
        scenario_id,
        scenario_npc_id,
        name,
        description,
        state,
        created_at
    )
    VALUES (
        gen_random_uuid(),
        NEW.session_id,
        NEW.scenario_id,
        gen_random_uuid(),
        'Guide NPC',
        'Initial guide character',
        '{
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
        NEW.started_at
    );

    RAISE NOTICE '[NPC] Initial NPCs created for session %', NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_07_initialize_npcs ON session;
CREATE TRIGGER trigger_07_initialize_npcs
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_npcs();
