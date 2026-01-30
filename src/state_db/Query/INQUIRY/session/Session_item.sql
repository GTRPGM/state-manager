-- --------------------------------------------------------------------
-- Session_item.sql
-- 세션 내 정의된 모든 아이템(마스터 데이터 인스턴스) 조회
-- API: GET /state/session/{session_id}/items
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    item_id,
    scenario_item_id,
    name,
    description,
    item_type,
    meta,
    created_at
FROM item
WHERE session_id = $1::uuid
ORDER BY name ASC;
