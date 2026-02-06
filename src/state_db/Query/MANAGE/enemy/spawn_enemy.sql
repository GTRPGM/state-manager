-- spawn_enemy.sql
-- Enemy 동적 생성 - Flattened
-- --------------------------------------------------------------------

INSERT INTO enemy (
    session_id,
    scenario_id,
    scenario_enemy_id,
    name,
    description,
    hp, max_hp, attack, defense,
    tags
)
SELECT
    $1::UUID,
    scenario_id,
    COALESCE($2::text, gen_random_uuid()::text),
    $3::text,
    COALESCE($4::text, ''),
    COALESCE($5, 100)::int,
    COALESCE($5, 100)::int,
    COALESCE($6, 10)::int,
    COALESCE($7, 5)::int,
    COALESCE($8, ARRAY['enemy']::TEXT[])
FROM session WHERE session_id = $1::UUID
RETURNING
    enemy_id AS id,
    name,
    description,
    tags,
    created_at;
