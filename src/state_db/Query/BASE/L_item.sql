-- ====================================================================
-- L_item.sql
-- 아이템 세션 초기화 로직 (Logic)
-- ====================================================================

CREATE OR REPLACE FUNCTION initialize_items()
RETURNS TRIGGER AS $$
DECLARE
    -- 마스터 데이터가 저장된 시스템 세션 ID (Session 0)
    MASTER_SESSION_ID CONSTANT UUID := '00000000-0000-0000-0000-000000000000';
BEGIN
    -- [Deep Copy] Session 0에 저장된 해당 시나리오의 원본 아이템 데이터를 신규 세션 ID로 복제 삽입
    INSERT INTO item (
        item_id,
        entity_type,
        session_id,
        scenario_id,
        scenario_item_id,
        name,
        description,
        item_type,
        meta,
        created_at
    )
    SELECT 
        gen_random_uuid(),  -- 복사본에 새로운 고유 ID 부여
        entity_type,
        NEW.session_id,     -- 트리거를 발생시킨 실제 세션 ID
        scenario_id,
        scenario_item_id,
        name,
        description,
        item_type,
        meta,
        NOW()
    FROM item
    WHERE session_id = MASTER_SESSION_ID 
      AND scenario_id = NEW.scenario_id;

    RAISE NOTICE '[Item] Initialized session % by cloning Master Items from Session 0', NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 설정
DROP TRIGGER IF EXISTS trigger_05_initialize_items ON session;
CREATE TRIGGER trigger_05_initialize_items
    AFTER INSERT ON session
    FOR EACH ROW
    -- 시스템 세션(Session 0) 자체 생성 시에는 복제를 수행하지 않음
    WHEN (NEW.session_id <> '00000000-0000-0000-0000-000000000000')
    EXECUTE FUNCTION initialize_items();