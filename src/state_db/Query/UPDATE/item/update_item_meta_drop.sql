-- update_item_meta_drop.sql
-- 아이템을 특정 시퀀스(필드)에 드롭 처리 (meta 업데이트 및 수량 합산)
UPDATE item
SET meta = meta || jsonb_build_object(
        'assigned_sequence_id', $1::text,
        'quantity', COALESCE((meta->>'quantity')::int, 0) + $3::int
    )
WHERE item_id = $2::uuid;
