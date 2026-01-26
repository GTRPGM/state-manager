-- --------------------------------------------------------------------
-- update_npc_affinity.sql
-- NPC 호감도 변경
-- 용도: 대화, 선물, 퀘스트 완료 등으로 호감도 변경
-- API: PUT /state/player/{player_id}/npc/{npc_id}/affinity
-- --------------------------------------------------------------------

-- 호감도 업데이트 (UPSERT 패턴)
INSERT INTO player_npc_relations (
    player_id,
    npc_id,
    affinity_score
)
VALUES (
    $1,  -- player_id
    $2,  -- npc_id
    GREATEST(0, LEAST(100, 50 + $3))  -- 초기값 50 + 변화량 (0-100 범위)
)
ON CONFLICT (player_id, npc_id)
DO UPDATE SET
    affinity_score = GREATEST(0, LEAST(100, player_npc_relations.affinity_score + $3)),
    updated_at = NOW()
RETURNING
    player_id,
    npc_id,
    affinity_score AS new_affinity,
    $3 AS affinity_change,
    interaction_count,
    last_interaction_at;

-- 파라미터:
-- $1: player_id (UUID)
-- $2: npc_id (UUID)
-- $3: affinity_change (INTEGER) - 호감도 변화량 (양수/음수)

-- 결과 예:
-- player_id | npc_id   | new_affinity | affinity_change | interaction_count
-- ----------|----------|--------------|-----------------|-------------------
-- uuid-123  | uuid-456 | 80           | 10              | 13

-- 사용 예:
-- 호감도 +10: affinity_change = 10
-- 호감도 -5:  affinity_change = -5
