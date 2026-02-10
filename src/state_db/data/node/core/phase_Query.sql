-- ====================================================================
-- Phase별 규칙 데이터 삽입
-- ====================================================================

INSERT INTO phase_rules (phase, description, rule_scope, allowed_actions)
VALUES
    (
        'exploration',
        '자유 탐색 및 환경 상호작용 단계',
        ARRAY['movement', 'perception', 'interaction'],
        ARRAY['move', 'inspect', 'talk', 'use_item']
    ),
    (
        'combat',
        '전투 규칙이 활성화되는 단계',
        ARRAY['initiative', 'attack', 'defense', 'damage'],
        ARRAY['attack', 'skill', 'defend', 'item']
    ),
    (
        'dialogue',
        '대화 중심 진행 단계',
        ARRAY['persuasion', 'deception', 'emotion'],
        ARRAY['talk', 'negotiate', 'threaten']
    ),
    (
        'rest',
        '회복 및 정비 단계',
        ARRAY['recovery', 'time_pass'],
        ARRAY['rest', 'heal', 'prepare']
    )
ON CONFLICT (phase) DO NOTHING;  -- 이미 존재하면 무시
