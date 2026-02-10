-- ====================================================================
-- player_inventory.sql
-- 플레이어 인벤토리 테이블 (플레이어-아이템 관계)
-- ====================================================================

CREATE TABLE IF NOT EXISTS player_inventory (
    -- 복합 키
    player_id UUID NOT NULL,
    item_id UUID NOT NULL,

    -- 수량
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity >= 0),

    -- 메타 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- 제약조건
    PRIMARY KEY (player_id, item_id),

    -- 외래키
    CONSTRAINT fk_player_inventory_player
        FOREIGN KEY (player_id)
        REFERENCES player(player_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_player_inventory_item
        FOREIGN KEY (item_id)
        REFERENCES item(item_id)
        ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_player_inventory_player_id ON player_inventory(player_id);
CREATE INDEX IF NOT EXISTS idx_player_inventory_item_id ON player_inventory(item_id);

-- updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_player_inventory_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_player_inventory_updated_at ON player_inventory;
CREATE TRIGGER trg_player_inventory_updated_at
BEFORE UPDATE ON player_inventory
FOR EACH ROW
EXECUTE FUNCTION update_player_inventory_updated_at();

-- session의 생성/종료에 맞춰 생성/삭제
CREATE OR REPLACE FUNCTION initialize_starting_items()
RETURNS TRIGGER AS $$
DECLARE
    v_player_id UUID;
    v_health_potion_id UUID;
BEGIN
    SELECT player_id INTO v_player_id
    FROM player
    WHERE session_id = NEW.session_id
    LIMIT 1;

    IF v_player_id IS NOT NULL THEN
        -- Health Potion 아이템 ID 조회
        SELECT item_id INTO v_health_potion_id
        FROM item
        WHERE session_id = NEW.session_id
          AND name = 'Health Potion'
        LIMIT 1;

        -- 초기 아이템 지급 (Health Potion x3)
        IF v_health_potion_id IS NOT NULL THEN
            INSERT INTO player_inventory (
                player_id,
                item_id,
                quantity,
                created_at
            )
            VALUES
            (
                v_player_id,
                v_health_potion_id,
                3,
                NEW.started_at
            );

            RAISE NOTICE '[Player Inventory] Starting items given to player % in session %',
                v_player_id, NEW.session_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_06_initialize_starting_items ON session;
CREATE TRIGGER trigger_06_initialize_starting_items
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_starting_items();


-- 주석
COMMENT ON TABLE player_inventory IS '플레이어 인벤토리 - 플레이어와 아이템의 관계 및 수량';
COMMENT ON COLUMN player_inventory.player_id IS '플레이어 ID';
COMMENT ON COLUMN player_inventory.item_id IS '아이템 ID';
COMMENT ON COLUMN player_inventory.quantity IS '보유 수량';
