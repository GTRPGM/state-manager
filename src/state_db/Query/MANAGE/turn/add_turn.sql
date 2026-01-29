-- [작업] RuleEngine 판정 후 상태 확정 시 호출
-- [기능] 1. session 테이블의 current_turn 1 증가
--       2. 증가된 번호로 turn 테이블에 신규 이력 생성
SELECT record_state_change(
    :session_id, 
    :turn_type,        -- 'action', 'event', 'system', 'combat_action' 등
    :state_changes,    -- JSONB 데이터 (예: '{"player_hp": -10, "gold": 50}')
    :related_entities  -- UUID[] (영향을 받은 엔티티 ID 배열, 생략 가능)
);