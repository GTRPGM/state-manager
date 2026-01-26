INSERT INTO enemy (
    enemy_id,
    session_id,
    scenario_id,
    scenario_enemy_id,
    name,
    description,
    tags,
    state
) VALUES (
    :enemy_id,
    :session_id,
    :scenario_id,
    :scenario_enemy_id,
    :name,
    :description,
    :tags,  -- 예: ARRAY['enemy', 'melee', 'goblin']
    jsonb_build_object(
        'numeric', jsonb_build_object(
            'HP', :HP,
            'MP', coalesce(:MP, 0),
            'STR', :STR,
            'DEX', :DEX,
            'INT', :INT,
            'LUX', null,
            'SAN', null
        ),
        'boolean', '{}'::jsonb
    )
)
RETURNING
    enemy_id,
    name,
    scenario_id,
    created_at;
