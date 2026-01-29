INSERT INTO npc (
    npc_id, name, description, session_id, scenario_id, scenario_npc_id, tags, state
) VALUES (
    gen_random_uuid(), $1, $2, '00000000-0000-0000-0000-000000000000', $3, $4, $5, $6
);
