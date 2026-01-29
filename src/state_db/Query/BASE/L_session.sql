
-- ====================================================================
-- 4. session 생성용 함수
-- ====================================================================

-- [외부 전달] scenario_id, act, sequence, location을 받아 session 생성
CREATE OR REPLACE FUNCTION create_session(
    p_scenario_id UUID,
    p_current_act INTEGER DEFAULT 1,
    p_current_sequence INTEGER DEFAULT 1,
    p_location TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    new_session_id UUID;
BEGIN
    INSERT INTO session (
        scenario_id,
        current_act,
        current_sequence,
        location,
        status,
        current_phase  -- 내부 관리: 기본값 'dialogue'
    )
    VALUES (
        p_scenario_id,
        p_current_act,
        p_current_sequence,
        p_location,
        'active',
        'dialogue'
    )
    RETURNING session_id INTO new_session_id;

    RETURN new_session_id;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 5. session 종료 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION end_session(p_session_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE session
    SET
        status = 'ended',
        ended_at = NOW()
    WHERE session_id = p_session_id
      AND status = 'active';

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 6. session 일시정지 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION pause_session(p_session_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE session
    SET
        status = 'paused',
        paused_at = NOW()
    WHERE session_id = p_session_id
      AND status = 'active';

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 7. session 재개 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION resume_session(p_session_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE session
    SET
        status = 'active',
        paused_at = NULL
    WHERE session_id = p_session_id
      AND status = 'paused';

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 8. Phase 변경 함수 (규칙 컨텍스트 전환)
-- ====================================================================

-- [내부 관리] Phase 변경 함수는 phase.sql에 정의되어 있음
-- change_phase(p_session_id UUID, p_new_phase phase_type) -> phase.sql 참조
--
-- Phase별 규칙 범위:
--   - exploration: movement, perception, interaction
--   - combat: initiative, attack, defense, damage
--   - dialogue: persuasion, deception, emotion
--   - rest: recovery, time_pass


-- ====================================================================
-- 9. Turn 진행 함수
-- ====================================================================

-- [내부 관리] Turn 진행 함수는 turn.sql에 정의되어 있음
-- advance_turn(p_session_id UUID) -> turn.sql 참조


-- ====================================================================
-- 10. Act/Sequence 진행 함수
-- ====================================================================

-- [외부 전달] Act/Sequence 업데이트 (시나리오 진행 단위)
--
-- 시나리오 진행 구조: story > act > sequence > scene > beat
-- GM 또는 시나리오 시스템에 의해 외부에서 호출됨

CREATE OR REPLACE FUNCTION update_act_sequence(
    p_session_id UUID,
    p_new_act INTEGER,
    p_new_sequence INTEGER
)
RETURNS RECORD AS $$
DECLARE
    result RECORD;
BEGIN
    UPDATE session
    SET
        current_act = p_new_act,
        current_sequence = p_new_sequence
    WHERE session_id = p_session_id
      AND status = 'active'
    RETURNING current_act, current_sequence INTO result;

    RAISE NOTICE 'Act/Sequence updated to %/% in session %',
        p_new_act, p_new_sequence, p_session_id;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 편의 함수: Sequence만 증가
CREATE OR REPLACE FUNCTION advance_sequence(p_session_id UUID)
RETURNS RECORD AS $$
DECLARE
    result RECORD;
BEGIN
    UPDATE session
    SET current_sequence = current_sequence + 1
    WHERE session_id = p_session_id
      AND status = 'active'
    RETURNING current_act, current_sequence INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 편의 함수: Act 증가 (Sequence는 1로 초기화)
CREATE OR REPLACE FUNCTION advance_act(p_session_id UUID)
RETURNS RECORD AS $$
DECLARE
    result RECORD;
BEGIN
    UPDATE session
    SET
        current_act = current_act + 1,
        current_sequence = 1  -- Act가 바뀌면 Sequence 초기화
    WHERE session_id = p_session_id
      AND status = 'active'
    RETURNING current_act, current_sequence INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 11. 현재 활성 session 조회 함수
-- ====================================================================

CREATE OR REPLACE FUNCTION get_active_sessions()
RETURNS TABLE (
    session_id UUID,
    scenario_id UUID,
    current_phase phase_type,
    current_act INTEGER,
    current_sequence INTEGER,
    current_turn INTEGER,
    location TEXT,
    started_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.session_id,
        s.scenario_id,
        s.current_phase,
        s.current_act,
        s.current_sequence,
        s.current_turn,
        s.location,
        s.started_at
    FROM session s
    WHERE s.status = 'active'
    ORDER BY s.started_at DESC;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 12. 주석 추가 (PostgreSQL 메타데이터)
-- ====================================================================

COMMENT ON TABLE session IS '플레이 세션 전역 컨테이너 - phase 중심 상태 관리';
COMMENT ON COLUMN session.session_id IS '플레이 세션 식별자';
COMMENT ON COLUMN session.scenario_id IS '진행 중인 시나리오 ID';
COMMENT ON COLUMN session.current_phase IS '현재 플레이 상태 (exploration/combat/dialogue/rest)';
COMMENT ON COLUMN session.current_act IS '현재 act 번호';
COMMENT ON COLUMN session.current_sequence IS '현재 sequence 번호';
COMMENT ON COLUMN session.current_turn IS '상태 확정 턴 카운터';
COMMENT ON COLUMN session.status IS '세션 상태 (active/paused/ended)';