-- [용도] 특정 아이템(예: 포션, 열쇠)이 충분히 있는지 확인
SELECT quantity
FROM player_inventory
WHERE player_id = :player_id AND item_id = :item_id;