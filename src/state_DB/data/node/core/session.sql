-- session.sql
-- 플레이 단위의 전역 컨테이너
--
-- 개념 구분:
--   [외부 전달] scenario_id, current_act, current_sequence, location
--   [내부 관리] current_phase (규칙 컨텍스트), current_turn (상태 확정 카운터)
--
-- current_phase: 선택 가능한 행동 단위 및 활성화 규칙 범위 결정
-- current_turn: 상태 변경 트랜잭션 commit 시마다 증가하는 카운터

-- ====================================================================
-- 1. ENUM 타입 정의
-- ====================================================================

-- Phase Enum 생성 (규칙 컨텍스트 정의)
DO $$ BEGIN
    CREATE TYPE phase_type AS ENUM (
        'exploration',  -- 자유 탐색 (movement, perception, interaction)
        'combat',       -- 전투 규칙 활성 (initiative, attack, defense, damage)
        'dialogue',     -- 대화 중심 (persuasion, deception, emotion)
        'rest'          -- 회복 및 정비 (recovery, time_pass)
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Session Status Enum 생성
DO $$ BEGIN
    CREATE TYPE session_status AS ENUM (
        'active',      -- 진행 중
        'paused',      -- 일시정지
        'ended'        -- 종료됨
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;


-- ====================================================================
-- 2. session 테이블 생성
-- ====================================================================

CREATE TABLE IF NOT EXISTS session (
    -- 식별자
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- [외부 전달] 시나리오 정보
    scenario_id UUID NOT NULL,
    -- FOREIGN KEY는 scenario 테이블 생성 후 추가
    -- CONSTRAINT fk_scenario FOREIGN KEY (scenario_id) REFERENCES scenario(scenario_id),

    -- [외부 전달] 시나리오 구조적 진행 단위 (story > act > sequence > scene > beat)
    current_act INTEGER NOT NULL DEFAULT 1 CHECK (current_act > 0),
    current_sequence INTEGER NOT NULL DEFAULT 1 CHECK (current_sequence > 0),

    -- [내부 관리] 규칙 컨텍스트 (Phase: 허용 행동 및 활성 규칙 범위 결정)
    current_phase phase_type NOT NULL DEFAULT 'dialogue',

    -- [내부 관리] 상태 확정 카운터 (Turn: 트랜잭션 commit 시마다 증가)
    current_turn INTEGER NOT NULL DEFAULT 0 CHECK (current_turn >= 0),

    -- [외부 전달] 위치 정보
    location TEXT,

    -- 세션 상태
    status session_status NOT NULL DEFAULT 'active',

    -- 타임스탬프
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP,
    paused_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_session_scenario_id ON session(scenario_id);
CREATE INDEX IF NOT EXISTS idx_session_status ON session(status);
CREATE INDEX IF NOT EXISTS idx_session_started_at ON session(started_at DESC);


-- ====================================================================
-- 3. 트리거 함수: updated_at 자동 업데이트
-- ====================================================================

CREATE OR REPLACE FUNCTION update_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 등록
DROP TRIGGER IF EXISTS trigger_update_session_timestamp ON session;
CREATE TRIGGER trigger_update_session_timestamp
    BEFORE UPDATE ON session
    FOR EACH ROW
    EXECUTE FUNCTION update_session_timestamp();


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

-- [내부 관리] Phase 변경 - 허용 행동 및 활성 규칙 범위 전환
--
-- Phase별 규칙 범위:
--   - exploration: movement, perception, interaction
--   - combat: initiative, attack, defense, damage
--   - dialogue: persuasion, deception, emotion
--   - rest: recovery, time_pass
--
-- GM 또는 RuleEngine에 의해 호출됨

CREATE OR REPLACE FUNCTION change_phase(
    p_session_id UUID,
    p_new_phase phase_type
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE session
    SET current_phase = p_new_phase
    WHERE session_id = p_session_id
      AND status = 'active';

    IF FOUND THEN
        RAISE NOTICE 'Phase changed to % in session %', p_new_phase, p_session_id;
    END IF;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;


-- ====================================================================
-- 9. Turn 진행 함수
-- ====================================================================

-- [내부 관리] 상태 변경 트랜잭션 commit 시 Turn 증가
--
-- Turn 증가 조건:
--   - RuleEngine 판정 결과로 State 변경이 확정될 때
--   - GM이 상태 적용을 승인(commit)했을 때
--   - Phase 전환으로 상태 스냅샷이 재계산될 때
--
-- Turn이 증가하지 않는 경우:
--   - 서술만 발생하고 상태 변경이 없는 경우
--   - 동일 상태의 재확인 또는 재서술
--   - 캐시 재동기화
--
CREATE OR REPLACE FUNCTION advance_turn(p_session_id UUID)
RETURNS INTEGER AS $$
DECLARE
    new_turn INTEGER;
BEGIN
    UPDATE session
    SET current_turn = current_turn + 1
    WHERE session_id = p_session_id
      AND status = 'active'
    RETURNING current_turn INTO new_turn;

    -- 로그: Turn 진행 기록
    RAISE NOTICE 'Turn advanced to % in session %', new_turn, p_session_id;

    RETURN new_turn;
END;
$$ LANGUAGE plpgsql;


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
