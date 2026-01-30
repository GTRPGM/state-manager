-- get_current_act_details.sql
-- 현재 세션의 Act 번호를 기반으로 시나리오 액트 상세 정보 조회

SELECT
    sa.scenario_id,
    sa.act_number,
    sa.title,
    sa.description,
    sa.metadata,
    sa.updated_at
FROM session s
JOIN scenario_act sa ON s.scenario_id = sa.scenario_id AND s.current_act = sa.act_number
WHERE s.session_id = $1;
