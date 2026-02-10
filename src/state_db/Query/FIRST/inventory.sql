CREATE TABLE IF NOT EXISTS inventory (
    -- inventory node ID
    inventory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 어느 세션에 속하는 inventory인지 (session 참조 포함)
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,

    -- 소유 엔티티 정보 (player / npc)
    owner_entity_type VARCHAR(20) NOT NULL
        CHECK (owner_entity_type IN ('player', 'npc')),

    owner_entity_id UUID NOT NULL, -- player.id 또는 npc.id 참조 가능 (외래키는 선택)

    -- inventory 상태 제약 (RuleEngine에서 참조)
    capacity INTEGER NULL,          -- 슬롯 수 제한 (null = 무제한)
    weight_limit NUMERIC NULL,      -- 무게 제한 (RuleEngine에서 계산)

    -- inventory 상태 플래그 (확장용) | 이거는 earn_item이랑 used_item으로 관리할듯?
    state JSONB DEFAULT '{}'::jsonb,  -- HP, 장착 상태, 기타 확장 가능

    -- meta 정보
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- 동일 세션에서 하나의 엔티티는 하나의 inventory만 가질 수 있음
    CONSTRAINT uq_inventory_owner UNIQUE (session_id, owner_entity_type, owner_entity_id)
);

-- updated_at 자동 갱신 트리거
CREATE OR REPLACE FUNCTION update_inventory_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_inventory_updated_at
BEFORE UPDATE ON inventory
FOR EACH ROW
EXECUTE FUNCTION update_inventory_updated_at();

-- session의 시작/종료에 의존한 inventory 생성/초기화
CREATE OR REPLACE FUNCTION initialize_player_inventory()
RETURNS TRIGGER AS $$
DECLARE
    v_player_id UUID;
BEGIN
    SELECT player_id INTO v_player_id
    FROM player
    WHERE session_id = NEW.session_id
    LIMIT 1;

    IF v_player_id IS NOT NULL THEN
        INSERT INTO inventory (
            session_id,
            owner_entity_type,
            owner_entity_id,
            capacity,
            weight_limit,
            created_at
        )
        VALUES (
            NEW.session_id,
            'player',
            v_player_id,
            NULL,
            NULL,
            NEW.started_at
        );

        RAISE NOTICE '[Inventory] Initial inventory created for player % in session %',
            v_player_id, NEW.session_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_04_initialize_inventory ON session;
CREATE TRIGGER trigger_04_initialize_inventory
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_player_inventory();
