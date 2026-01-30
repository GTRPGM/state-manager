-- ====================================================================
-- B_player_inventory.sql
-- 플레이어 인벤토리 관계 테이블 (Base)
-- ====================================================================

CREATE TABLE IF NOT EXISTS player_inventory (
    -- 복합 키 (플레이어와 아이템의 N:M 관계)
    player_id UUID NOT NULL,
    item_id INT NOT NULL,

    -- 수량
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity >= 0),

    -- 메타 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- 제약조건
    PRIMARY KEY (player_id, item_id),

    -- 외래키 (B_player.sql 선행 필요)
    CONSTRAINT fk_player_inventory_player
        FOREIGN KEY (player_id)
        REFERENCES player(player_id)
        ON DELETE CASCADE
    -- item FK 제거: item PK가 (item_id, session_id) 복합키이므로
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_player_inventory_player_id ON player_inventory(player_id);
CREATE INDEX IF NOT EXISTS idx_player_inventory_item_id ON player_inventory(item_id);

-- updated_at 자동 갱신 트리거 함수
CREATE OR REPLACE FUNCTION update_player_inventory_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 등록
DROP TRIGGER IF EXISTS trg_player_inventory_updated_at ON player_inventory;
CREATE TRIGGER trg_player_inventory_updated_at
BEFORE UPDATE ON player_inventory
FOR EACH ROW
EXECUTE FUNCTION update_player_inventory_updated_at();

-- 주석
COMMENT ON TABLE player_inventory IS '플레이어 인벤토리 - 플레이어와 아이템의 관계 및 수량';
COMMENT ON COLUMN player_inventory.player_id IS '플레이어 ID';
COMMENT ON COLUMN player_inventory.item_id IS '아이템 ID';
COMMENT ON COLUMN player_inventory.quantity IS '보유 수량';