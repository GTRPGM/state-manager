-- B_scenario_act.sql
-- 시나리오 내 각 액트(Act)의 상세 메타데이터 정의

CREATE TABLE IF NOT EXISTS scenario_act (
    scenario_id UUID NOT NULL REFERENCES scenario(scenario_id) ON DELETE CASCADE,
    act_id VARCHAR(100) NOT NULL, -- 예: 'act-1'
    act_name VARCHAR(200) NOT NULL,
    act_description TEXT,
    exit_criteria TEXT, -- 다음 액트로 넘어가기 위한 조건

    sequence_ids TEXT[], -- 해당 액트에 포함된 시퀀스 ID 리스트
    metadata JSONB DEFAULT '{}'::jsonb,

    PRIMARY KEY (scenario_id, act_id)
);

COMMENT ON TABLE scenario_act IS '시나리오의 진행 단계(Act)별 상세 정보 및 조건 관리';
