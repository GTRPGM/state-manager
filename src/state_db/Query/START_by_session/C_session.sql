-- ####################################################################
-- [작업영역 1] SESSION 생성 및 초기화
-- ####################################################################

-- --------------------------------------------------------------------
-- 1-1. 새 Session 생성
-- 용도: 게임 시작 시 호출
-- API: POST /state/session/start
-- --------------------------------------------------------------------

-- 기본 세션 생성 (scenario_id만 전달)
SELECT create_session(
    '550e8400-e29b-41d4-a716-446655440000'::UUID  -- scenario_id
);

-- 전체 파라미터를 지정한 세션 생성
SELECT create_session(
    '550e8400-e29b-41d4-a716-446655440000'::UUID,  -- scenario_id
    1,                                               -- current_act
    1,                                               -- current_sequence
    'Starting Town'                                  -- location
);

-- 반환값: session_id (UUID)
-- 예: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'


-- --------------------------------------------------------------------
-- 1-2. Session 생성 확인 (생성된 데이터 조회)
-- 용도: 세션이 제대로 생성되었는지 확인
-- --------------------------------------------------------------------

-- 특정 session 조회
SELECT
    session_id,
    scenario_id,
    current_act,
    current_sequence,
    current_phase,
    current_turn,
    location,
    status,
    started_at
FROM session
WHERE session_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'::UUID;

-- 생성된 player 확인 (트리거로 자동 생성됨)
SELECT
    player_id,
    session_id,
    name,
    hp,
    max_hp,
    gold
FROM player
WHERE session_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'::UUID;


-- --------------------------------------------------------------------
-- 1-3. 활성 Session 목록 조회
-- 용도: 현재 진행 중인 게임 세션 확인
-- API: GET /state/sessions/active
-- --------------------------------------------------------------------

SELECT * FROM get_active_sessions();

-- 또는 직접 쿼리
SELECT
    session_id,
    scenario_id,
    current_phase,
    current_act,
    current_sequence,
    current_turn,
    location,
    started_at
FROM session
WHERE status = 'active'
ORDER BY started_at DESC;
