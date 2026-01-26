INSERT INTO player (
    session_id,
    name,
    description,
    state
) VALUES (
    :session_id,
    :name,
    :description,
    jsonb_build_object(
        'numeric', jsonb_build_object(
            'HP', 100,
            'MP', 50,
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
    id AS player_id,
    name,
    session_id,
    created_at;
