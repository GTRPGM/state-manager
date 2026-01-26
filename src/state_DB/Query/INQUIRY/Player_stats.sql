-- --------------------------------------------------------------------
-- Player_stats.sql
-- 플레이어 상세 스탯 조회
-- 용도: 플레이어의 모든 상태 정보 확인
-- API: GET /state/player/{player_id}
-- --------------------------------------------------------------------

SELECT
    player_id,
    entity_type,
    name,
    description,
    session_id,
    state,
    relations,
    tags,
    created_at,
    updated_at
FROM player
WHERE player_id = $1;

-- 결과 예:
-- player_id | name | state                                              | relations
-- ----------|------|----------------------------------------------------|-----------
-- uuid-123  | Hero | {"numeric": {"HP": 85, "MP": 50, ...}, "boolean": {}} | [...]
