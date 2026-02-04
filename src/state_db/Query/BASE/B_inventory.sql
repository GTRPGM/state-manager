-- ====================================================================
-- B_inventory.sql
-- 인벤토리 관리 테이블 구조 (Base)
-- ====================================================================

CREATE TABLE IF NOT EXISTS inventory (
    -- inventory node ID
    inventory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 어느 세션에 속하는 inventory인지
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,

    -- 소유 엔티티 정보 (player / npc)
    owner_entity_type VARCHAR(20) NOT NULL
        CHECK (owner_entity_type IN ('player', 'npc')),

    owner_entity_id UUID NOT NULL, -- player.id 또는 npc.id 참조 가능

    -- inventory 상태 제약
    capacity INTEGER NULL,          -- 슬롯 수 제한 (null = 무제한)
    weight_limit NUMERIC NULL,      -- 무게 제한

    -- inventory 상태 플래그 (확장용)
    state JSONB DEFAULT '{}'::jsonb,

    -- meta 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- 동일 세션에서 하나의 엔티티는 하나의 inventory만 가질 수 있음
    CONSTRAINT uq_inventory_owner UNIQUE (session_id, owner_entity_type, owner_entity_id)
);

-- updated_at 자동 갱신 트리거 함수
CREATE OR REPLACE FUNCTION update_inventory_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 등록
DROP TRIGGER IF EXISTS trg_inventory_updated_at ON inventory;
CREATE TRIGGER trg_inventory_updated_at
BEFORE UPDATE ON inventory
FOR EACH ROW
EXECUTE FUNCTION update_inventory_updated_at();

-- 주석 추가
COMMENT ON TABLE inventory IS '세션 내 엔티티(Player/NPC)별 인벤토리 관리 테이블';
