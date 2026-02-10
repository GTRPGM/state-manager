-- [작업] 호감도 수치 변경 및 통합 턴 기록
-- [설명] 트리거에 의해 interaction_count는 자동 증가됩니다.

BEGIN;

-- 1. 호감도 수정
UPDATE player_npc_relations
SET affinity_score = GREATEST(0, LEAST(100, affinity_score + :change_amount)),
    relation_type = :new_relation_type -- 필요 시 (예: 80점 이상이면 'friendly')
WHERE player_id = :player_id AND npc_id = :npc_id;

-- 2. 통합 턴 기록
SELECT record_state_change(
    :session_id,
    'social_interaction',
    jsonb_build_object(
        'npc_id', :npc_id,
        'affinity_change', :change_amount,
        'message', (SELECT name FROM npc WHERE npc_id = :npc_id) || '와의 관계가 변화했습니다.'
    ),
    ARRAY[:player_id, :npc_id]::UUID[]
);

COMMIT;
