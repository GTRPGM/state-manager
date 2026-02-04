-- ====================================================================
-- L_turn.sql
-- 상태 변화 기반 턴 카운팅 및 관리 로직 (Logic)
-- ====================================================================

-- 1. 상태 변화 기록 및 턴 전진 함수
-- RuleEngine에서 상태 변화가 발생할 때 호출하여 턴을 1씩 올리고 내용을 기록합니다.
CREATE OR REPLACE FUNCTION record_state_change(
    p_session_id UUID,
    p_turn_type VARCHAR(50),
    p_state_changes JSONB,
    p_entities UUID[] DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_next_turn INTEGER;
    v_current_phase phase_type;
BEGIN
    -- [Logic] 세션 테이블의 current_turn을 1 증가시키고 현재 정보를 가져옴
    UPDATE session
    SET current_turn = current_turn + 1
    WHERE session_id = p_session_id AND status = 'active'
    RETURNING current_turn, current_phase INTO v_next_turn, v_current_phase;

    -- [Logic] 증가된 턴 번호와 함께 상세 내역을 turn 테이블에 기록
    IF v_next_turn IS NOT NULL THEN
        INSERT INTO turn (
            turn_id,
            session_id,
            turn_number,
            phase_at_turn,
            turn_type,
            state_changes,
            related_entities
        )
        VALUES (
            gen_random_uuid(),
            p_session_id,
            v_next_turn,
            v_current_phase,
            p_turn_type,
            p_state_changes,
            p_entities
        );
    END IF;

    RETURN v_next_turn;
END;
$$ LANGUAGE plpgsql;

-- 2. 세션 초기화 시 0번 턴(초기 상태) 기록 트리거
CREATE OR REPLACE FUNCTION initialize_turn()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO turn (
        turn_id,
        session_id,
        turn_number,
        phase_at_turn,
        turn_type,
        state_changes,
        created_at
    )
    VALUES (
        gen_random_uuid(),
        NEW.session_id,
        0, -- 시작 지점은 0턴으로 정의
        NEW.current_phase,
        'initial_state',
        '{}'::jsonb,
        NEW.started_at
    );

    RAISE NOTICE '[Turn] Session initialized at turn 0 for session %', NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_02_initialize_turn ON session;
CREATE TRIGGER trigger_02_initialize_turn
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_turn();
