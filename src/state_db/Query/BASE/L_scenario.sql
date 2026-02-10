-- 세션 생성 시 Enemy를 시나리오 원본으로부터 복사하는 함수
CREATE OR REPLACE FUNCTION initialize_enemies()
RETURNS TRIGGER AS $$
DECLARE
    -- session_id 0을 UUID 형식으로 선언
    system_session_id UUID := '00000000-0000-0000-0000-000000000000';
BEGIN
    -- [핵심] Session 0 데이터를 새 세션으로 복사
    INSERT INTO enemy (
        enemy_id,
        entity_type,
        name,
        description,
        session_id,
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
        gen_random_uuid(),
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
    WHERE session_id = system_session_id  -- 변수명 일치시킴
      AND scenario_id = NEW.scenario_id;

    RAISE NOTICE '[Enemy] Initial enemies setup from Master (Session 0) for session %', NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 연결
DROP TRIGGER IF EXISTS trigger_08_initialize_enemies ON session;
CREATE TRIGGER trigger_08_initialize_enemies
    AFTER INSERT ON session
    FOR EACH ROW
    -- 0번 세션 자체 생성 시에는 동작 방지
    WHEN (NEW.session_id <> '00000000-0000-0000-0000-000000000000')
    EXECUTE FUNCTION initialize_enemies();
