-- ====================================================================
-- L_enemy.sql
-- Enemy 세션 초기화 및 복제 로직 (Logic)
-- ====================================================================

CREATE OR REPLACE FUNCTION initialize_enemies()
RETURNS TRIGGER AS $$
DECLARE
    -- 마스터 데이터가 저장된 시스템 세션 ID (Session 0)
    MASTER_SESSION_ID CONSTANT UUID := '00000000-0000-0000-0000-000000000000';
BEGIN
    -- [Deep Copy] Session 0에 저장된 원본 Enemy 데이터를 신규 세션 ID로 복제 삽입
    INSERT INTO enemy (
        enemy_id,
        entity_type,
        name,
        description,
        session_id,         -- 신규 생성된 세션 ID 적용
        scenario_id,
        scenario_enemy_id,
        tags,
        state,
        relations,
        dropped_items,
        created_at,
        updated_at
    )
    SELECT 
        gen_random_uuid(),  -- 복사본은 새로운 고유 ID 생성
        entity_type,
        name,
        description,
        NEW.session_id,     -- 대상 세션 ID
        scenario_id,
        scenario_enemy_id,
        tags,
        state,
        relations,
        dropped_items,
        NOW(),
        NOW()
    FROM enemy
    WHERE session_id = MASTER_SESSION_ID 
      AND scenario_id = NEW.scenario_id;

    RAISE NOTICE '[Enemy] Initialized session % by cloning Master Data from Session 0', NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 설정: session 테이블에 신규 세션 INSERT 발생 시 실행
DROP TRIGGER IF EXISTS trigger_08_initialize_enemies ON session;
CREATE TRIGGER trigger_08_initialize_enemies
    AFTER INSERT ON session
    FOR EACH ROW
    -- 시스템 세션(Session 0) 자체 생성 시에는 복제를 수행하지 않음
    WHEN (NEW.session_id <> '00000000-0000-0000-0000-000000000000')
    EXECUTE FUNCTION initialize_enemies();