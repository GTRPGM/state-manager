INSERT INTO item (
    item_id, name, description, session_id, scenario_id, scenario_item_id, item_type, meta
) VALUES (
    $1, $2, $3, '00000000-0000-0000-0000-000000000000', $4, $1, $5, $6
);
-- Master 데이터는 item_id와 scenario_item_id를 동일하게 설정하여 원형임을 표시합니다.