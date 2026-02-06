-- --------------------------------------------------------------------
-- record_item_use.sql
-- 아이템 사용 기록을 turn 테이블에 추가
-- $1: session_id, $2: player_id, $3: item_id(state_entity_id), $4: quantity_used, $5: remaining_quantity
-- --------------------------------------------------------------------

WITH session_info AS (
    SELECT
        s.session_id,
        s.current_turn + 1 AS new_turn_number
    FROM session s
    WHERE s.session_id = $1::uuid
      AND s.status = 'active'
),
update_turn AS (
    UPDATE session
    SET current_turn = current_turn + 1
    FROM session_info si
    WHERE session.session_id = si.session_id
)
INSERT INTO turn (
    session_id,
    turn_number,
    turn_type,
    state_changes,
    related_entities
)
SELECT
    si.session_id,
    si.new_turn_number,
    'item_use',
    jsonb_build_object(
        'action', 'use_item',
        'item_id', $3::text,
        'quantity_used', $4::int,
        'remaining_quantity', $5::int
    ),
    ARRAY[$2::uuid]
FROM session_info si
RETURNING
    turn_id::text,
    turn_number,
    state_changes;
