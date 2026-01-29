-- --------------------------------------------------------------------
-- spawn_npc.sql
-- NPC 동적 생성
-- --------------------------------------------------------------------

INSERT INTO npc (
    session_id,
    scenario_id,
    scenario_npc_id,
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
            'MP', 50
        ),
        'boolean', '{}'::jsonb
    ),
    COALESCE($6, ARRAY['npc']::TEXT[])
FROM session WHERE session_id = $1::UUID
RETURNING
    npc_id AS id,
    name,
    description,
    state,
    tags,
    created_at;
