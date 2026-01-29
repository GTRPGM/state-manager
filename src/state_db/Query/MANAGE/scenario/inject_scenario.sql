INSERT INTO scenario (
    scenario_id, title, description, author, version, difficulty, genre, tags, total_acts, is_published
) VALUES (
    gen_random_uuid(), $1, $2, $3, $4, $5, $6, $7, $8, true
) RETURNING scenario_id;
