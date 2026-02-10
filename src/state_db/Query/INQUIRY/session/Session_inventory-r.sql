-- --------------------------------------------------------------------
-- Session_inventory.sql
-- 세션의 플레이어 인벤토리 조회
-- 용도: 현재 세션의 플레이어가 보유한 아이템 목록 확인
-- API: GET /state/session/{session_id}/inventory
-- --------------------------------------------------------------------

SELECT
    pi.player_id,
    pi.item_id,
    pi.quantity,
    pi.created_at AS acquired_at,
    pi.updated_at AS last_updated
FROM player_inventory pi
JOIN player p ON pi.player_id = p.player_id
WHERE p.session_id = $1
  AND pi.quantity > 0
ORDER BY pi.created_at ASC;

-- 결과 예:
-- player_id | item_id | quantity | acquired_at         | last_updated
-- ----------|---------|----------|---------------------|---------------------
-- uuid-123  | 1       | 3        | 2026-01-23 10:00:00 | 2026-01-23 10:05:00
-- uuid-123  | 5       | 1        | 2026-01-23 10:15:00 | 2026-01-23 10:15:00
