-- B_scenario_sequence.sql
-- 시나리오 내 각 시퀀스(Sequence)의 상세 메타데이터 및 전환 조건 정의

CREATE TABLE IF NOT EXISTS scenario_sequence (
    scenario_id UUID NOT NULL REFERENCES scenario(scenario_id) ON DELETE CASCADE,
    sequence_id VARCHAR(100) NOT NULL, -- 예: 'seq-1'
    sequence_name VARCHAR(200) NOT NULL,
    location_name VARCHAR(200), -- 해당 시퀀스의 구체적인 장소명
    description TEXT,
    goal TEXT,

    exit_triggers JSONB DEFAULT '[]'::jsonb, -- 전환 조건 리스트
    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (scenario_id, sequence_id)
);

COMMENT ON TABLE scenario_sequence IS '시나리오의 세부 진행 단위(Sequence)별 목표 및 탈출 조건 관리';
