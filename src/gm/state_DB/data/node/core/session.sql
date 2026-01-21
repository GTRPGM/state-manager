-- session.sql
-- 플레이 단위의 전역 컨테이너
-- 모든 상태 판정, 로그, 캐시의 기준점

CREATE TABLE IF NOT EXISTS session (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 진행 중인 시나리오
    scenario_id UUID NOT NULL,

    -- 세션 상태
    status VARCHAR(20) NOT NULL DEFAULT 'playing',

    -- 구조적 진행 단위
    current_act INTEGER NOT NULL DEFAULT 1,
    current_sequence INTEGER NOT NULL DEFAULT 1,

    -- 규칙 컨텍스트
    current_phase VARCHAR(30) NOT NULL DEFAULT 'exploration',

    -- 상태 확정 카운터 (Turn Concept)
    current_turn INTEGER NOT NULL DEFAULT 0,

    -- 위치 정보 (선택적)
    location TEXT,

    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
