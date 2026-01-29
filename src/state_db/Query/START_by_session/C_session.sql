-- create_session 함수를 사용하여 세션 생성 (Enemy 자동 복제 트리거 발생)
SELECT create_session(
    :scenario_id, 
    :current_act, 
    :current_sequence, 
    :location
);