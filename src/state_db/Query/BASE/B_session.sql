-- B_session.sql
-- 1. ENUM 타입 정의
DO $$ BEGIN
    CREATE TYPE phase_type AS ENUM ('exploration', 'combat', 'dialogue', 'rest');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE session_status AS ENUM ('active', 'paused', 'ended');
EXCEPTION WHEN duplicate_object THEN null; END $$;

-- 2. session 테이블 생성
CREATE TABLE IF NOT EXISTS session (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES scenario(scenario_id) ON DELETE RESTRICT,

    -- [기존 유지] 숫자 기반 카운터
    current_act INTEGER NOT NULL DEFAULT 1,
    current_sequence INTEGER NOT NULL DEFAULT 1,

    -- [신규 추가] 가이드 준수 문자열 ID
    current_act_id VARCHAR(100) DEFAULT 'act-1',
    current_sequence_id VARCHAR(100) DEFAULT 'seq-1',

    -- 규칙 컨텍스트
    current_phase phase_type NOT NULL DEFAULT 'dialogue',
    current_turn INTEGER NOT NULL DEFAULT 0,

    location TEXT,
    status session_status NOT NULL DEFAULT 'active',

    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP,
    paused_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_session_scenario_id ON session(scenario_id);
CREATE INDEX IF NOT EXISTS idx_session_status ON session(status);

CREATE OR REPLACE FUNCTION update_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_session_timestamp ON session;
CREATE TRIGGER trigger_update_session_timestamp
    BEFORE UPDATE ON session
    FOR EACH ROW
    EXECUTE FUNCTION update_session_timestamp();

-- 시스템 마스터 세션 (Session 0)
INSERT INTO session (session_id, scenario_id, current_act, current_sequence, status, location)
VALUES ('00000000-0000-0000-0000-000000000000', '00000000-0000-0000-0000-000000000000', 1, 1, 'active', 'SYSTEM_MASTER_LOCATION')
ON CONFLICT (session_id) DO NOTHING;
