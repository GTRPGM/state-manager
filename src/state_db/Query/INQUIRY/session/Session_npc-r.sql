-- Session_npc.sql
-- 현재 세션의 '위치'와 '시퀀스'에 맞는 NPC들만 조회

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
