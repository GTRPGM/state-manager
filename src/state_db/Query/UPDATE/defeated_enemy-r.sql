-- 적 패배(사망) 처리
-- $1: enemy_instance_id, $2: session_id
-- is_active 컬럼이 없으므로 HP를 0으로 만들고 태그에 'defeated' 추가
UPDATE enemy
SET state = jsonb_set(state, '{numeric, HP}', '0'::jsonb),
    tags = array_append(tags, 'defeated')
WHERE enemy_id = $1 AND session_id = $2
RETURNING
    enemy_id AS enemy_instance_id,
    'defeated' AS status;
