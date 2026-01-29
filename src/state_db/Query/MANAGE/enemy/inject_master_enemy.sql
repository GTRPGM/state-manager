-- inject_master_enemy.sql
INSERT INTO enemy (
    enemy_id, name, description, scenario_id, scenario_enemy_id, session_id, assigned_sequence_id, assigned_location, tags, state, dropped_items
) VALUES (
    gen_random_uuid(), $1, $2, $3, $4, '00000000-0000-0000-0000-000000000000', $5, $6, $7, $8, $9
);
