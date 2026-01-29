-- inject_master_item.sql
INSERT INTO item (
    item_id, name, description, session_id, scenario_id, scenario_item_id, item_type, meta
) VALUES (
    gen_random_uuid(), $1, $2, '00000000-0000-0000-0000-000000000000', $3, gen_random_uuid(), $4, $5
);
