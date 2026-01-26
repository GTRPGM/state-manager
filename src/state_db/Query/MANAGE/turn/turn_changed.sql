-- --------------------------------------------------------------------
-- 4-2. Turn 진행 후 상태 변경 기록
-- 용도: Turn에서 어떤 상태 변경이 있었는지 기록
-- --------------------------------------------------------------------

-- Turn에 상태 변경 내용 업데이트
SELECT update_turn_state_changes(
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890'::UUID,  -- session_id
    6,                                               -- turn_number
    '{"player_hp": -10, "enemy_hp": -20, "gold": 50}'::jsonb,  -- state_changes
    'combat_action'                                  -- turn_type
);
