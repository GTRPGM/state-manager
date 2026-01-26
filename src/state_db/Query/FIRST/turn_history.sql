-- turn_history.sql
-- Turn별 상태 변경 이력 추적 테이블

-- ====================================================================
-- 1. turn_history 테이블
-- ====================================================================

CREATE TABLE IF NOT EXISTS turn_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    -- FOREIGN KEY (session_id) REFERENCES session(session_id) ON DELETE CASCADE,

    -- Turn 정보
    turn_number INTEGER NOT NULL,

    -- 해당 Turn의 Phase 컨텍스트
    phase_at_turn phase_type NOT NULL,

    -- Turn 증가 원인
    turn_type VARCHAR(50) NOT NULL,  -- 'state_change', 'phase_transition', 'gm_commit' 등

    -- 상태 변경 요약 (JSONB)
    state_changes JSONB,  -- {"player_hp": -10, "inventory_added": [1, 3], "gold": +50} 등

    -- 관련 엔티티 (선택적)
    related_entities UUID[],  -- 영향받은 player, npc, enemy ID들

    -- 타임스탬프
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_turn_history_session_id ON turn_history(session_id);
CREATE INDEX IF NOT EXISTS idx_turn_history_turn_number ON turn_history(session_id, turn_number);
CREATE INDEX IF NOT EXISTS idx_turn_history_created_at ON turn_history(created_at DESC);

COMMENT ON TABLE turn_history IS 'Turn별 상태 변경 이력 추적 (트랜잭션 단위 기록)';


-- ====================================================================
-- 2. Turn 증가 시 자동 기록 트리거
-- ====================================================================

CREATE OR REPLACE FUNCTION log_turn_advance()
RETURNS TRIGGER AS $$
BEGIN
    -- Turn이 증가한 경우에만 기록
    IF NEW.current_turn > OLD.current_turn THEN
        INSERT INTO turn_history (
            session_id,
            turn_number,
            phase_at_turn,
            turn_type,
            state_changes
        )
        VALUES (
            NEW.session_id,
            NEW.current_turn,
            NEW.current_phase,
            'auto',  -- 기본값 (나중에 업데이트 가능)
            '{}'::jsonb  -- 빈 객체 (나중에 업데이트)
        );

        RAISE NOTICE '[Turn History] Turn % recorded in session %',
            NEW.current_turn, NEW.session_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 등록 (session 테이블에)
DROP TRIGGER IF EXISTS trigger_log_turn_advance ON session;
CREATE TRIGGER trigger_log_turn_advance
    AFTER UPDATE ON session
    FOR EACH ROW
    WHEN (NEW.current_turn > OLD.current_turn)
    EXECUTE FUNCTION log_turn_advance();


-- ====================================================================
-- 3. Turn 이력 업데이트 함수 (상태 변경 기록용)
-- ====================================================================

-- Turn에 상태 변경 내용 추가 기록
CREATE OR REPLACE FUNCTION update_turn_state_changes(
    p_session_id UUID,
    p_turn_number INTEGER,
    p_state_changes JSONB,
    p_turn_type VARCHAR(50) DEFAULT 'state_change'
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE turn_history
    SET
        state_changes = p_state_changes,
        turn_type = p_turn_type
    WHERE session_id = p_session_id
      AND turn_number = p_turn_number;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 4. Turn 이력 조회 함수
-- ====================================================================

-- 특정 세션의 Turn 이력 조회
CREATE OR REPLACE FUNCTION get_turn_history(p_session_id UUID)
RETURNS TABLE (
    turn_number INTEGER,
    phase_at_turn phase_type,
    turn_type VARCHAR,
    state_changes JSONB,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        th.turn_number,
        th.phase_at_turn,
        th.turn_type,
        th.state_changes,
        th.created_at
    FROM turn_history th
    WHERE th.session_id = p_session_id
    ORDER BY th.turn_number ASC;
END;
$$ LANGUAGE plpgsql;

-- 특정 Turn의 상태 변경 조회
CREATE OR REPLACE FUNCTION get_turn_details(
    p_session_id UUID,
    p_turn_number INTEGER
)
RETURNS TABLE (
    turn_number INTEGER,
    phase_at_turn phase_type,
    turn_type VARCHAR,
    state_changes JSONB,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        th.turn_number,
        th.phase_at_turn,
        th.turn_type,
        th.state_changes,
        th.created_at
    FROM turn_history th
    WHERE th.session_id = p_session_id
      AND th.turn_number = p_turn_number;
END;
$$ LANGUAGE plpgsql;

-- Turn 범위로 조회 (리플레이 기능용)
CREATE OR REPLACE FUNCTION get_turn_range(
    p_session_id UUID,
    p_start_turn INTEGER,
    p_end_turn INTEGER
)
RETURNS TABLE (
    turn_number INTEGER,
    phase_at_turn phase_type,
    turn_type VARCHAR,
    state_changes JSONB,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        th.turn_number,
        th.phase_at_turn,
        th.turn_type,
        th.state_changes,
        th.created_at
    FROM turn_history th
    WHERE th.session_id = p_session_id
      AND th.turn_number BETWEEN p_start_turn AND p_end_turn
    ORDER BY th.turn_number ASC;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 5. Turn 통계 함수
-- ====================================================================

-- Phase별 Turn 수 집계
CREATE OR REPLACE FUNCTION get_turns_per_phase(p_session_id UUID)
RETURNS TABLE (
    phase phase_type,
    turn_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        th.phase_at_turn AS phase,
        COUNT(*) AS turn_count
    FROM turn_history th
    WHERE th.session_id = p_session_id
    GROUP BY th.phase_at_turn
    ORDER BY turn_count DESC;
END;
$$ LANGUAGE plpgsql;

-- 평균 Turn 소요 시간
CREATE OR REPLACE FUNCTION get_average_turn_duration(p_session_id UUID)
RETURNS INTERVAL AS $$
DECLARE
    total_duration INTERVAL;
    turn_count INTEGER;
BEGIN
    SELECT
        MAX(created_at) - MIN(created_at),
        COUNT(*)
    INTO total_duration, turn_count
    FROM turn_history
    WHERE session_id = p_session_id;

    IF turn_count > 0 THEN
        RETURN total_duration / turn_count;
    ELSE
        RETURN INTERVAL '0';
    END IF;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 6. 리플레이 기능 (Turn 되돌리기)
-- ====================================================================

-- 특정 Turn으로 상태 복원 (개념적 구현)
CREATE OR REPLACE FUNCTION replay_to_turn(
    p_session_id UUID,
    p_target_turn INTEGER
)
RETURNS JSONB AS $$
DECLARE
    turn_data RECORD;
    replay_result JSONB;
BEGIN
    -- 해당 Turn까지의 모든 상태 변경을 순차적으로 적용
    -- (실제 구현 시 복잡한 롤백 로직 필요)

    SELECT jsonb_agg(
        jsonb_build_object(
            'turn', turn_number,
            'phase', phase_at_turn,
            'changes', state_changes
        ) ORDER BY turn_number
    ) INTO replay_result
    FROM turn_history
    WHERE session_id = p_session_id
      AND turn_number <= p_target_turn;

    RETURN replay_result;
END;
$$ LANGUAGE plpgsql;
