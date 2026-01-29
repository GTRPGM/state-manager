-- 신규 세션 생성 (이 쿼리 하나로 트리거가 작동하여 Player, Turn 0, Phase 0, Enemy 복제가 연쇄 발생)
INSERT INTO session (session_id, scenario_id, current_phase, status)
VALUES ('{target_session_uuid}', '{target_scenario_uuid}', 'exploration', 'active');