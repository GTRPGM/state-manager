-- [작업] 아이템 사용 및 소모 내역 기록
-- [제약] 보유 수량이 사용량보다 적으면 업데이트가 실패하여 턴이 진행되지 않음

BEGIN;

-- 1. 수량 차감 (수량 부족 시 0개 행 수정됨)
UPDATE player_inventory
SET
    quantity = quantity - :amount,
    updated_at = NOW()
WHERE player_id = :player_id
  AND item_id = :item_id
  AND quantity >= :amount;

-- 2. 통합 턴 기록 및 전진
-- rule_id 등 GM의 판단 근거를 state_changes에 기록
SELECT record_state_change(
    :session_id,
    'use_item',
    jsonb_build_object(
        'inventory_lost', ARRAY[:item_id],
        'lost_quantity', :amount,
        'rule_id', :rule_id,
        'message', (SELECT name FROM item WHERE item_id = :item_id) || '을(를) 사용했습니다.'
    ),
    ARRAY[:player_id, :item_id]::UUID[]
);

COMMIT;
