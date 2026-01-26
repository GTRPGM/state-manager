INSERT INTO npc (
    npc_id,
    session_id,
    scenario_id,
    scenario_npc_id,
    name,
    description,
    tags,
    state
) VALUES (
    :npc_id,
    :session_id,
    :scenario_id,
    :scenario_npc_id,
    :name,
    :description,
    :tags,  -- 예: ARRAY['npc', 'merchant', 'quest_giver']
    jsonb_build_object(
        'numeric', jsonb_build_object(
            'HP', :HP,
            'MP', :MP,
            'STR', :STR,
            'DEX', :DEX,
            'INT', :INT,
            'LUX', :LUX,
            'SAN', :SAN
        ),
        'boolean', '{}'::jsonb
    )
)
RETURNING
    npc_id,
    name,
    scenario_id,
    created_at;
