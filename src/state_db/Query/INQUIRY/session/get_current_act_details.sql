-- get_current_act_details.sql
-- 현재 세션의 Act ID를 기반으로 시나리오 액트 상세 정보 조회

SELECT
    sa.scenario_id,
    sa.act_id,
    sa.act_name,
    sa.act_description,
    sa.exit_criteria,
    sa.sequence_ids,
    sa.metadata
FROM session s
JOIN scenario_act sa ON s.scenario_id = sa.scenario_id AND s.current_act_id = sa.act_id
WHERE s.session_id = $1;
