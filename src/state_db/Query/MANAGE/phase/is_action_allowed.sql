-- --------------------------------------------------------------------
-- 3-3. 특정 행동이 허용되는지 검증
-- 용도: RuleEngine이 플레이어 행동 검증
-- --------------------------------------------------------------------

-- 'attack' 행동이 현재 Phase에서 허용되는지 확인
SELECT is_action_allowed(
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890'::UUID,  -- session_id
    'attack'                                         -- action
);

-- 반환값: BOOLEAN
-- combat phase: true
-- dialogue phase: false
