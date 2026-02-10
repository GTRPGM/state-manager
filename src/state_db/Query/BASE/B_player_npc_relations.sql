-- ====================================================================
-- B_player_npc_relations.sql
-- 플레이어-NPC 관계 테이블 구조 (Base)
-- ====================================================================

DROP TABLE IF EXISTS player_npc_relations CASCADE;

CREATE TABLE player_npc_relations (
    -- 복합 키 (플레이어와 NPC의 1:1 관계를 세션 내에서 정의)
    player_id UUID NOT NULL,
    npc_id UUID NOT NULL,

    -- 호감도 (0-100)
    affinity_score INTEGER NOT NULL DEFAULT 50 CHECK (affinity_score BETWEEN 0 AND 100),

    -- 관계 상태
    relation_type VARCHAR(50) DEFAULT 'neutral', -- neutral, friendly, hostile 등

    -- 상호작용 기록
    interaction_count INTEGER NOT NULL DEFAULT 0,
    last_interaction_at TIMESTAMP,

    -- 메타 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- 제약조건
    PRIMARY KEY (player_id, npc_id),

    -- 외래키 (B_player.sql 및 B_npc.sql 선행 필요)
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

-- 주석
COMMENT ON TABLE player_npc_relations IS '플레이어-NPC 관계 및 호감도 관리 테이블';
