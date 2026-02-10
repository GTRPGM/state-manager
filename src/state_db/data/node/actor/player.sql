CREATE TABLE IF NOT EXISTS player (
    -- 엔티티 필수
    player_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL DEFAULT 'player',
    name VARCHAR(20) NOT NULL,
    description TEXT DEFAULT '',

    -- session 자동 참조
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,

    -- meta 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    tags TEXT[] DEFAULT ARRAY['player']::TEXT[],

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

    -- RELATION 엣지 ID 저장 (relation_id 배열)
    relations JSONB DEFAULT '[]'::jsonb,

    -- session.started_at과 동기화 보장
    CONSTRAINT fk_player_session FOREIGN KEY (session_id)
        REFERENCES session(session_id) ON DELETE CASCADE
);


-- 2. updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_player_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_player_updated_at ON player;
CREATE TRIGGER trg_player_updated_at
BEFORE UPDATE ON player
FOR EACH ROW
EXECUTE FUNCTION update_player_updated_at();

-- 3. created_at을 session.started_at과 동기화하는 트리거
CREATE OR REPLACE FUNCTION initialize_player()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO player (
        session_id,
        name,
        description,
        state,
        created_at
    )
    VALUES (
        NEW.session_id,
        'Player',
        'Default player character',
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

    RAISE NOTICE '[Player] Initial player created for session %', NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_03_initialize_player ON session;
CREATE TRIGGER trigger_03_initialize_player
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_player();
