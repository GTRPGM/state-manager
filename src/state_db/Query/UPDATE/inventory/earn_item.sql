-- [작업] 아이템 습득 및 턴/로그 통합 기록
-- [설명] 인벤토리에 수량을 반영하고, record_state_change를 통해 턴을 넘깁니다.

BEGIN;

-- 1. 인벤토리 수량 반영 (UPSERT)
INSERT INTO player_inventory (player_id, item_id, quantity)
VALUES (:player_id, :item_id, :amount)
ON CONFLICT (player_id, item_id)
DO UPDATE SET 
    quantity = player_inventory.quantity + EXCLUDED.quantity,
    updated_at = NOW();

-- 2. 통합 턴 기록 및 전진
-- state_changes에 습득 정보를, related_entities에 관련 ID를 포함
SELECT record_state_change(
    :session_id, 
    'item_acquisition', 
    jsonb_build_object(
        'inventory_added', ARRAY[:item_id],
        'added_quantity', :amount,
        'message', (SELECT name FROM item WHERE item_id = :item_id) || '을(를) 얻었습니다.'
    ),
    ARRAY[:player_id, :item_id]::UUID[]
);

COMMIT;