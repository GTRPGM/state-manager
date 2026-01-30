SELECT 
    s.current_phase AS session_current,
    p.new_phase AS history_latest
FROM session s
JOIN phase p ON s.session_id = p.session_id
WHERE s.session_id = $1
ORDER BY p.transitioned_at DESC
LIMIT 1;