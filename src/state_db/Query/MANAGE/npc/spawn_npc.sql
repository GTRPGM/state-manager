-- --------------------------------------------------------------------
-- spawn_npc.sql
-- NPC 동적 생성 - Flattened
-- --------------------------------------------------------------------

INSERT INTO npc (
    session_id,
    scenario_id,
    scenario_npc_id,
    name,
    description,
    hp, mp, san,
    tags
)
SELECT
    $1::UUID,
    scenario_id,
    COALESCE($2::text, gen_random_uuid()::text),
    $3::text,
    COALESCE($4::text, ''),
    COALESCE($5, 100)::int,
    50, 10,
    COALESCE($6, ARRAY['npc']::TEXT[])
FROM session WHERE session_id = $1::UUID
RETURNING
    npc_id AS id,
    name,
    description,
    tags,
    created_at;
