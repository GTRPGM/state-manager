-- [용도] 플레이어가 보유한 모든 아이템 이름, 설명, 수량 조회
-- [설명] 아이템(item) 테이블과 조인하여 상세 정보를 함께 표시
SELECT
    i.name,
    i.description,
    pi.quantity,
    i.item_type,
    i.state AS item_state
FROM player_inventory pi
JOIN item i ON pi.item_id = i.item_id
WHERE pi.player_id = :player_id;
