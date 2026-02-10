-- get_current_sequence_details.sql
-- 현재 세션의 Sequence ID를 기반으로 시나리오 시퀀스 상세 정보 조회

SELECT
    ss.scenario_id,
    ss.sequence_id,
    ss.sequence_name,
    ss.location_name,
    ss.description,
    ss.goal,
    ss.exit_triggers,
    ss.metadata,
    ss.created_at,
    ss.updated_at
FROM session s
JOIN scenario_sequence ss ON s.scenario_id = ss.scenario_id AND s.current_sequence_id = ss.sequence_id
WHERE s.session_id = $1;
