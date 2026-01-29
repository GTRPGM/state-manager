-- --------------------------------------------------------------------
-- Session_inventory.sql
-- 세션의 플레이어 인벤토리 조회
-- 용도: 현재 세션의 플레이어가 보유한 아이템 목록 확인
-- API: GET /state/session/{session_id}/inventory
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    pi.player_id,
    pi.item_id,
    i.name AS item_name,
    i.description,
    pi.quantity,
    i.item_type AS category,
    i.meta AS item_state,
    pi.created_at AS acquired_at
FROM player_inventory pi
JOIN player p ON pi.player_id = p.player_id
LEFT JOIN item i ON pi.item_id = i.item_id
WHERE p.session_id = $1
  AND pi.quantity > 0
ORDER BY pi.created_at ASC;
