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

    -- scenario 테이블 참조
    CONSTRAINT fk_session_scenario
        FOREIGN KEY (scenario_id)
        REFERENCES scenario(scenario_id)
        ON DELETE RESTRICT,  -- 시나리오 삭제 시 활성 세션이 있으면 삭제 방지

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
-- [핵심 추가] 시스템 마스터 세션 (Session 0) 생성
-- ====================================================================
-- 시나리오 원형(마스터 데이터)들이 소속될 가상 세션입니다.
-- scenario_id 역시 B_scenario에서 생성할 시스템 마스터 ID('000...0')를 참조합니다.

INSERT INTO session (
    session_id, 
    scenario_id, 
    current_act, 
    current_sequence, 
    current_phase, 
    status,
    location
) VALUES (
    '00000000-0000-0000-0000-000000000000', 
    '00000000-0000-0000-0000-000000000000', 
    1, 
    1, 
    'dialogue', 
    'active',
    'SYSTEM_MASTER_LOCATION'
) ON CONFLICT (session_id) DO NOTHING;

-- 6. 주석 추가
COMMENT ON TABLE session IS '플레이 세션 전역 컨테이너 - phase 중심 상태 관리';    