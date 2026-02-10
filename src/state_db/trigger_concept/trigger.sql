-- session_initialization_trigger.sql
-- session 생성 시 자동으로 player, inventory 등을 초기화

-- ====================================================================
-- 1. session 초기화 트리거 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION initialize_session_data()
RETURNS TRIGGER AS $$
DECLARE
    new_player_id UUID;
BEGIN
    -- 1. 기본 플레이어 생성 (시나리오별 초기 설정은 별도 처리 가능)
    INSERT INTO player (
        session_id,
        name,
        hp,
        max_hp,
        gold
    )
    VALUES (
        NEW.session_id,
        'Hero',  -- 기본 이름 (나중에 업데이트 가능)
        100,     -- 초기 HP
        100,     -- 최대 HP
        0        -- 초기 골드
    )
    RETURNING player_id INTO new_player_id;

    -- 2. 기본 인벤토리 아이템 추가 (선택적)
    -- 예: 초기 아이템 지급 (item_id 1번: 포션)
    -- INSERT INTO player_inventory (player_id, item_id, quantity)
    -- VALUES (new_player_id, 1, 3);

    -- 3. 로그 기록 (선택적)
    RAISE NOTICE 'Session % initialized with player %', NEW.session_id, new_player_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 2. 트리거 등록
-- ====================================================================

DROP TRIGGER IF EXISTS trigger_initialize_session ON session;
CREATE TRIGGER trigger_initialize_session
    AFTER INSERT ON session
    FOR EACH ROW
    WHEN (NEW.status = 'active')  -- active 상태로 생성될 때만
    EXECUTE FUNCTION initialize_session_data();


-- ====================================================================
-- 3. session 종료 시 정리 트리거 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION cleanup_session_on_end()
RETURNS TRIGGER AS $$
BEGIN
    -- session이 종료되면 관련 임시 데이터 정리 (선택적)
    -- 예: 전투 중인 적 삭제
    DELETE FROM enemy
    WHERE session_id = NEW.session_id;

    -- 로그 기록
    RAISE NOTICE 'Session % ended and cleaned up', NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 4. 트리거 등록 (종료 시)
-- ====================================================================

DROP TRIGGER IF EXISTS trigger_cleanup_session ON session;
CREATE TRIGGER trigger_cleanup_session
    AFTER UPDATE ON session
    FOR EACH ROW
    WHEN (OLD.status != 'ended' AND NEW.status = 'ended')
    EXECUTE FUNCTION cleanup_session_on_end();


-- ====================================================================
-- 5. phase 변경 시 검증 트리거 (선택적)
-- ====================================================================

CREATE OR REPLACE FUNCTION validate_phase_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Phase 전환 규칙 검증 (예시)
    -- combat -> rest는 허용하지 않음
    IF OLD.current_phase = 'combat' AND NEW.current_phase = 'rest' THEN
        RAISE EXCEPTION 'Cannot transition from combat to rest directly';
    END IF;

    -- 로그 기록
    IF OLD.current_phase != NEW.current_phase THEN
        RAISE NOTICE 'Phase changed: % -> % in session %',
            OLD.current_phase, NEW.current_phase, NEW.session_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 6. 트리거 등록 (phase 변경 검증)
-- ====================================================================

DROP TRIGGER IF EXISTS trigger_validate_phase ON session;
CREATE TRIGGER trigger_validate_phase
    BEFORE UPDATE ON session
    FOR EACH ROW
    WHEN (OLD.current_phase IS DISTINCT FROM NEW.current_phase)
    EXECUTE FUNCTION validate_phase_transition();


-- ====================================================================
-- 7. session 스냅샷 자동 생성 함수 (일시정지 시)
-- ====================================================================

CREATE OR REPLACE FUNCTION create_session_snapshot()
RETURNS TRIGGER AS $$
DECLARE
    snapshot_data JSONB;
BEGIN
    -- session 전체 상태를 JSONB로 캡처
    SELECT jsonb_build_object(
        'session', row_to_json(NEW),
        'players', (
            SELECT jsonb_agg(row_to_json(p))
            FROM player p
            WHERE p.session_id = NEW.session_id
        ),
        'inventories', (
            SELECT jsonb_agg(row_to_json(i))
            FROM player_inventory i
            JOIN player p ON i.player_id = p.player_id
            WHERE p.session_id = NEW.session_id
        ),
        'npc_relations', (
            SELECT jsonb_agg(row_to_json(r))
            FROM player_npc_relations r
            JOIN player p ON r.player_id = p.player_id
            WHERE p.session_id = NEW.session_id
        ),
        'npcs', (
            SELECT jsonb_agg(row_to_json(n))
            FROM npc n
            WHERE n.session_id = NEW.session_id
        ),
        'enemies', (
            SELECT jsonb_agg(row_to_json(e))
            FROM enemy e
            WHERE e.session_id = NEW.session_id
        )
    ) INTO snapshot_data;

    -- 스냅샷 저장
    INSERT INTO session_snapshot (session_id, snapshot_data, snapshot_type)
    VALUES (NEW.session_id, snapshot_data, 'auto');

    RAISE NOTICE 'Snapshot created for session %', NEW.session_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 8. 트리거 등록 (일시정지 시 스냅샷)
-- ====================================================================

DROP TRIGGER IF EXISTS trigger_create_snapshot ON session;
CREATE TRIGGER trigger_create_snapshot
    AFTER UPDATE ON session
    FOR EACH ROW
    WHEN (OLD.status = 'active' AND NEW.status = 'paused')
    EXECUTE FUNCTION create_session_snapshot();
