-- ====================================================================
-- player_npc_relations.sql
-- 플레이어-NPC 관계 테이블 (호감도 시스템)
-- ====================================================================

CREATE TABLE IF NOT EXISTS player_npc_relations (
    -- 복합 키
    player_id UUID NOT NULL,
    npc_id UUID NOT NULL,

    -- 호감도 (0-100)
    affinity_score INTEGER NOT NULL DEFAULT 50 CHECK (affinity_score BETWEEN 0 AND 100),

    -- 관계 상태 (선택적)
    relation_type VARCHAR(50) DEFAULT 'neutral',  -- neutral, friendly, hostile, romantic 등

    -- 상호작용 기록
    interaction_count INTEGER NOT NULL DEFAULT 0,
    last_interaction_at TIMESTAMP,

    -- 메타 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- 제약조건
    PRIMARY KEY (player_id, npc_id),

    -- 외래키
    CONSTRAINT fk_player_npc_relations_player
        FOREIGN KEY (player_id)
        REFERENCES player(player_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_player_npc_relations_npc
        FOREIGN KEY (npc_id)
        REFERENCES npc(npc_id)
        ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_player_npc_relations_player_id ON player_npc_relations(player_id);
CREATE INDEX IF NOT EXISTS idx_player_npc_relations_npc_id ON player_npc_relations(npc_id);
CREATE INDEX IF NOT EXISTS idx_player_npc_relations_affinity ON player_npc_relations(affinity_score);

-- updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_player_npc_relations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_player_npc_relations_updated_at ON player_npc_relations;
CREATE TRIGGER trg_player_npc_relations_updated_at
BEFORE UPDATE ON player_npc_relations
FOR EACH ROW
EXECUTE FUNCTION update_player_npc_relations_updated_at();

-- 상호작용 시 자동으로 카운터 증가 및 시간 기록
CREATE OR REPLACE FUNCTION update_npc_interaction()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.affinity_score IS DISTINCT FROM NEW.affinity_score THEN
        NEW.interaction_count = OLD.interaction_count + 1;
        NEW.last_interaction_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_npc_interaction ON player_npc_relations;
CREATE TRIGGER trg_npc_interaction
BEFORE UPDATE ON player_npc_relations
FOR EACH ROW
EXECUTE FUNCTION update_npc_interaction();

-- session의 생성/종료에 맞춰서 생성/삭제
CREATE OR REPLACE FUNCTION initialize_npc_relations()
RETURNS TRIGGER AS $$
DECLARE
    v_player_id UUID;
    v_npc_record RECORD;
BEGIN
    SELECT player_id INTO v_player_id
    FROM player
    WHERE session_id = NEW.session_id
    LIMIT 1;

    IF v_player_id IS NOT NULL THEN
        FOR v_npc_record IN
            SELECT npc_id FROM npc WHERE session_id = NEW.session_id
        LOOP
            INSERT INTO player_npc_relations (
                player_id,
                npc_id,
                affinity_score,
                relation_type,
                created_at
            )
            VALUES (
                v_player_id,
                v_npc_record.npc_id,
                50,
                'neutral',
                NEW.started_at
            );
        END LOOP;

        RAISE NOTICE '[NPC Relations] Initial NPC relations created for player % in session %',
            v_player_id, NEW.session_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_09_initialize_npc_relations ON session;
CREATE TRIGGER trigger_09_initialize_npc_relations
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_npc_relations();

-- 주석
COMMENT ON TABLE player_npc_relations IS '플레이어-NPC 관계 테이블 (호감도 및 상호작용 기록)';
COMMENT ON COLUMN player_npc_relations.affinity_score IS 'NPC 호감도 (0-100)';
COMMENT ON COLUMN player_npc_relations.relation_type IS '관계 유형 (neutral, friendly, hostile 등)';
COMMENT ON COLUMN player_npc_relations.interaction_count IS '총 상호작용 횟수';
