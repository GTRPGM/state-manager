INSERT INTO enemy (enemy_id, session_id, scenario_id, scenario_enemy_id, name, state)
VALUES (gen_random_uuid(), :session_id, :scenario_id, :scenario_enemy_id, :name, :state_json);