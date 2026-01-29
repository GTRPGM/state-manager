SELECT scenario_id, title, difficulty, genre, tags, total_acts 
FROM scenario 
WHERE is_published = true AND is_active = true
ORDER BY created_at DESC;