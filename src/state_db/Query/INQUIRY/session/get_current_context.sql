-- get_current_context.sql
-- 현재 세션의 Act ID와 Sequence ID를 기반으로 모든 맥락 정보 조회

SELECT
    s.session_id,
    -- Act 정보
    sa.act_id,
    sa.act_name,
    sa.act_description,
    sa.exit_criteria AS act_exit_criteria,
    -- Sequence 정보
    ss.sequence_id,
    ss.sequence_name,
    ss.location_name,
    ss.description AS sequence_description,
    ss.goal AS sequence_goal,
    ss.exit_triggers AS sequence_exit_triggers
FROM session s
JOIN scenario_act sa ON s.scenario_id = sa.scenario_id AND s.current_act_id = sa.act_id
JOIN scenario_sequence ss ON s.scenario_id = ss.scenario_id AND s.current_sequence_id = ss.sequence_id
WHERE s.session_id = $1;
