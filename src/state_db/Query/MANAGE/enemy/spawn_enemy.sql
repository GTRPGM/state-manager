-- spawn_enemy.sql
-- Enemy 동적 생성
-- --------------------------------------------------------------------

INSERT INTO enemy (
    session_id,
    scenario_id,
    scenario_enemy_id,
    name,
    description,
    state,
    tags
)
SELECT
    $1::UUID,
    scenario_id,
    COALESCE($2::text, gen_random_uuid()::text)::UUID,
    $3::text,
    COALESCE($4::text, ''),
    jsonb_build_object(
        'numeric', jsonb_build_object(
            'HP', COALESCE($5, 100)::int,
            'attack', COALESCE($6, 10)::int,
            'defense', COALESCE($7, 5)::int
        ),
        'boolean', '{}'::jsonb
    ),
    COALESCE($8, ARRAY['enemy']::TEXT[])
FROM session WHERE session_id = $1::UUID
RETURNING
    enemy_id AS id,
    name,
    description,
    state,
    tags,
    created_at;
