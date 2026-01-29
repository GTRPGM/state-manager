-- inject_master_npc.sql
INSERT INTO npc (
    npc_id, name, description, scenario_id, scenario_npc_id, session_id, assigned_sequence_id, assigned_location, tags, state
) VALUES (
    gen_random_uuid(), $1, $2, $3, $4, '00000000-0000-0000-0000-000000000000', $5, $6, $7, $8
);
