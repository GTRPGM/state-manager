-- --------------------------------------------------------------------
-- Session_npc.sql
-- 세션의 NPC 목록 조회
-- $1: session_id
-- --------------------------------------------------------------------

SELECT
    n.npc_id,
    n.scenario_npc_id,
    n.name,
    n.description,
    n.state,
    n.tags,
    n.assigned_location,
    n.assigned_sequence_id
FROM npc n
JOIN session s ON n.session_id = s.session_id
WHERE s.session_id = $1
  AND (
      n.assigned_sequence_id = s.current_sequence_id
      OR
      n.assigned_location = s.location
  );