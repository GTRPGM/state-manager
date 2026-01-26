-- ====================================================================
-- session_dml.sql
-- Session 관련 모든 DML 쿼리 통합 파일
-- 작업영역별로 주석으로 구분되어 있음
-- ====================================================================


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


-- ####################################################################
-- [작업영역 2] SESSION 상태 조회
-- ####################################################################

-- --------------------------------------------------------------------
-- 2-1. Session 전체 정보 조회
-- 용도: GM이 현재 세션 상태 확인
-- API: GET /state/session/{session_id}
-- --------------------------------------------------------------------

SELECT
    session_id,
    scenario_id,

    -- 시나리오 진행 단위 (외부 전달)
    current_act,
    current_sequence,
    location,

    -- 내부 관리 단위
    current_phase,
    current_turn,

    -- 세션 상태
    status,
    started_at,
    ended_at,
    paused_at,
    created_at,
    updated_at
FROM session
WHERE session_id = $1;


-- --------------------------------------------------------------------
-- 2-2. Session의 현재 Phase 정보 조회
-- 용도: RuleEngine이 현재 허용되는 행동 확인
-- --------------------------------------------------------------------

-- 현재 Phase 조회
SELECT current_phase
FROM session
WHERE session_id = $1;

-- 현재 Phase의 허용 행동 조회
SELECT get_session_allowed_actions($1);

-- 결과 예: {move, inspect, talk, use_item}


-- --------------------------------------------------------------------
-- 2-3. Session의 현재 Turn 정보 조회
-- 용도: 상태 변경 트랜잭션의 기준점 확인
-- --------------------------------------------------------------------

SELECT current_turn
FROM session
WHERE session_id = $1;


-- --------------------------------------------------------------------
-- 2-4. Session 기본 통계
-- 용도: 대시보드 표시
-- --------------------------------------------------------------------

SELECT
    session_id,
    current_phase,
    current_turn,

    -- 세션 진행 시간
    NOW() - started_at AS session_duration,

    -- Phase별 Turn 수 (서브쿼리)
    (SELECT COUNT(*) FROM turn_history th
     WHERE th.session_id = s.session_id
       AND th.phase_at_turn = 'combat') AS combat_turns,

    (SELECT COUNT(*) FROM turn_history th
     WHERE th.session_id = s.session_id
       AND th.phase_at_turn = 'exploration') AS exploration_turns
FROM session s
WHERE session_id = $1;


-- ####################################################################
-- [작업영역 3] PHASE 관리 (내부 관리)
-- ####################################################################

-- --------------------------------------------------------------------
-- 3-1. Phase 변경
-- 용도: GM 또는 RuleEngine이 Phase 전환
-- API: PUT /state/session/{session_id}/phase
-- --------------------------------------------------------------------

-- Phase 변경 함수 호출
SELECT change_phase(
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890'::UUID,  -- session_id
    'combat'::phase_type                             -- new_phase
);

-- 반환값: BOOLEAN (성공: true, 실패: false)


-- --------------------------------------------------------------------
-- 3-2. Phase 변경 후 확인
-- 용도: Phase가 제대로 변경되었는지 확인
-- --------------------------------------------------------------------

SELECT current_phase
FROM session
WHERE session_id = $1;

-- Phase 변경 이력 확인
SELECT * FROM get_phase_history($1)
ORDER BY transitioned_at DESC
LIMIT 5;


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


-- --------------------------------------------------------------------
-- 3-4. Phase 통계 조회
-- 용도: 게임 분석 및 밸런싱
-- --------------------------------------------------------------------

-- Phase별 소요 시간 및 전환 횟수
SELECT * FROM get_phase_statistics($1);

-- 결과 예:
-- phase       | total_duration | transition_count
-- ------------|----------------|------------------
-- combat      | 01:20:00       | 3
-- exploration | 00:45:00       | 2
-- dialogue    | 00:30:00       | 1

-- 현재 Phase 지속 시간
SELECT get_current_phase_duration($1);

-- 결과 예: 00:15:30


-- ####################################################################
-- [작업영역 4] TURN 관리 (내부 관리)
-- ####################################################################

-- --------------------------------------------------------------------
-- 4-1. Turn 진행 (상태 변경 트랜잭션 commit 시)
-- 용도: RuleEngine 판정 후 상태 확정 시 호출
-- --------------------------------------------------------------------

-- Turn 증가 함수 호출
SELECT advance_turn($1);  -- session_id

-- 반환값: 새로운 turn_number (INTEGER)
-- 예: 6


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


-- --------------------------------------------------------------------
-- 4-3. Turn 이력 조회
-- 용도: 게임 리플레이, 디버깅
-- API: GET /state/session/{session_id}/turns
-- --------------------------------------------------------------------

-- 전체 Turn 이력
SELECT * FROM get_turn_history($1)
ORDER BY turn_number ASC;

-- 특정 Turn 상세 조회
SELECT * FROM get_turn_details($1, 5);  -- session_id, turn_number

-- Turn 범위 조회 (1~10번 Turn)
SELECT * FROM get_turn_range($1, 1, 10);


-- --------------------------------------------------------------------
-- 4-4. Turn 통계
-- 용도: 게임 분석
-- --------------------------------------------------------------------

-- Phase별 Turn 수
SELECT * FROM get_turns_per_phase($1);

-- 결과 예:
-- phase       | turn_count
-- ------------|------------
-- combat      | 15
-- exploration | 8
-- dialogue    | 3

-- 평균 Turn 소요 시간
SELECT get_average_turn_duration($1);

-- 결과 예: 00:02:30 (Turn당 평균 2분 30초)


-- ####################################################################
-- [작업영역 5] ACT/SEQUENCE 관리 (외부 전달)
-- ####################################################################

-- --------------------------------------------------------------------
-- 5-1. Act/Sequence 직접 업데이트
-- 용도: GM 또는 시나리오 시스템이 진행 단위 변경
-- API: PUT /state/session/{session_id}/progress
-- --------------------------------------------------------------------

-- Act와 Sequence를 모두 지정
SELECT update_act_sequence(
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890'::UUID,  -- session_id
    2,                                               -- new_act
    3                                                -- new_sequence
);

-- 반환값: RECORD (current_act, current_sequence)


-- --------------------------------------------------------------------
-- 5-2. Sequence만 증가
-- 용도: 같은 Act 내에서 Sequence 진행
-- --------------------------------------------------------------------

SELECT advance_sequence($1);  -- session_id

-- 반환값: RECORD (current_act, current_sequence)
-- 예: (2, 4) - Act 2, Sequence 4


-- --------------------------------------------------------------------
-- 5-3. Act 증가 (Sequence는 1로 초기화)
-- 용도: 다음 Act로 진행
-- --------------------------------------------------------------------

SELECT advance_act($1);  -- session_id

-- 반환값: RECORD (current_act, current_sequence)
-- 예: (3, 1) - Act 3, Sequence 1


-- --------------------------------------------------------------------
-- 5-4. 현재 Act/Sequence 조회
-- 용도: UI 표시
-- --------------------------------------------------------------------

SELECT
    current_act,
    current_sequence
FROM session
WHERE session_id = $1;


-- ####################################################################
-- [작업영역 6] LOCATION 관리 (외부 전달)
-- ####################################################################

-- --------------------------------------------------------------------
-- 6-1. Location 업데이트
-- 용도: 플레이어 위치 변경
-- API: PUT /state/session/{session_id}/location
-- --------------------------------------------------------------------

UPDATE session
SET location = $2  -- new_location
WHERE session_id = $1
  AND status = 'active';

-- 파라미터:
-- $1: session_id
-- $2: 'Forest Entrance'


-- --------------------------------------------------------------------
-- 6-2. 현재 Location 조회
-- 용도: UI 표시
-- --------------------------------------------------------------------

SELECT location
FROM session
WHERE session_id = $1;


-- ####################################################################
-- [작업영역 7] SESSION 일시정지/재개/종료
-- ####################################################################

-- --------------------------------------------------------------------
-- 7-1. Session 일시정지 (스냅샷 자동 생성)
-- 용도: 게임 임시 중단
-- API: POST /state/session/{session_id}/pause
-- --------------------------------------------------------------------

SELECT pause_session($1);  -- session_id

-- 반환값: BOOLEAN
-- 트리거로 자동으로 session_snapshot 생성됨


-- --------------------------------------------------------------------
-- 7-2. 생성된 스냅샷 확인
-- 용도: 일시정지 시점 데이터 확인
-- --------------------------------------------------------------------

SELECT
    snapshot_id,
    session_id,
    snapshot_type,
    created_at,
    snapshot_data  -- JSONB
FROM session_snapshot
WHERE session_id = $1
ORDER BY created_at DESC
LIMIT 1;


-- --------------------------------------------------------------------
-- 7-3. Session 재개
-- 용도: 일시정지된 게임 재개
-- API: POST /state/session/{session_id}/resume
-- --------------------------------------------------------------------

SELECT resume_session($1);  -- session_id

-- 반환값: BOOLEAN


-- --------------------------------------------------------------------
-- 7-4. Session 종료
-- 용도: 게임 완전 종료
-- API: POST /state/session/{session_id}/end
-- --------------------------------------------------------------------

SELECT end_session($1);  -- session_id

-- 반환값: BOOLEAN
-- 트리거로 자동으로 enemy 데이터 정리됨


-- --------------------------------------------------------------------
-- 7-5. Session 상태별 조회
-- 용도: 관리 대시보드
-- --------------------------------------------------------------------

-- 활성 세션
SELECT session_id, scenario_id, started_at
FROM session
WHERE status = 'active'
ORDER BY started_at DESC;

-- 일시정지된 세션
SELECT session_id, scenario_id, paused_at
FROM session
WHERE status = 'paused'
ORDER BY paused_at DESC;

-- 종료된 세션
SELECT session_id, scenario_id, started_at, ended_at
FROM session
WHERE status = 'ended'
ORDER BY ended_at DESC;


-- ####################################################################
-- [작업영역 8] 복합 쿼리 (여러 테이블 조인)
-- ####################################################################

-- --------------------------------------------------------------------
-- 8-1. Session + Player 통합 조회
-- 용도: 게임 전체 상태 조회
-- API: GET /state/session/{session_id}/full
-- --------------------------------------------------------------------

SELECT
    -- Session 정보
    s.session_id,
    s.scenario_id,
    s.current_act,
    s.current_sequence,
    s.current_phase,
    s.current_turn,
    s.location,
    s.status,

    -- Player 정보
    p.player_id,
    p.name AS player_name,
    p.hp,
    p.max_hp,
    p.gold,

    -- 통계
    (SELECT COUNT(*) FROM player_inventory pi WHERE pi.player_id = p.player_id) AS item_count,
    (SELECT COUNT(*) FROM player_npc_relations pnr WHERE pnr.player_id = p.player_id) AS npc_relation_count
FROM session s
LEFT JOIN player p ON s.session_id = p.session_id
WHERE s.session_id = $1;


-- --------------------------------------------------------------------
-- 8-2. Session + Phase History 조회
-- 용도: Phase 전환 흐름 분석
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.current_phase,
    ph.previous_phase,
    ph.new_phase,
    ph.turn_at_transition,
    ph.transitioned_at
FROM session s
LEFT JOIN phase_history ph ON s.session_id = ph.session_id
WHERE s.session_id = $1
ORDER BY ph.transitioned_at ASC;


-- --------------------------------------------------------------------
-- 8-3. Session + Turn History 조회
-- 용도: 게임 진행 타임라인
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.current_turn,
    th.turn_number,
    th.phase_at_turn,
    th.turn_type,
    th.state_changes,
    th.created_at
FROM session s
LEFT JOIN turn_history th ON s.session_id = th.session_id
WHERE s.session_id = $1
ORDER BY th.turn_number ASC;


-- ####################################################################
-- [작업영역 9] 트랜잭션 예시 (상태 변경 + Turn 증가)
-- ####################################################################

-- --------------------------------------------------------------------
-- 9-1. 전투 행동 처리 (완전한 트랜잭션)
-- 용도: RuleEngine이 전투 판정 후 상태 적용
-- --------------------------------------------------------------------

BEGIN;

-- 1. 플레이어 HP 감소
UPDATE player
SET hp = hp - 10
WHERE player_id = 'player_uuid'
  AND session_id = 'session_uuid';

-- 2. 적 HP 감소
UPDATE enemy
SET hp = hp - 20
WHERE enemy_instance_id = 'enemy_uuid'
  AND session_id = 'session_uuid';

-- 3. Turn 증가
SELECT advance_turn('session_uuid');

-- 4. Turn 상태 변경 기록
SELECT update_turn_state_changes(
    'session_uuid',
    (SELECT current_turn FROM session WHERE session_id = 'session_uuid'),
    '{"player_hp": -10, "enemy_hp": -20}'::jsonb,
    'combat_action'
);

-- 5. 로그 기록 (선택적)
-- INSERT INTO play_log ...

COMMIT;


-- --------------------------------------------------------------------
-- 9-2. 아이템 획득 처리
-- 용도: 탐색 중 아이템 발견
-- --------------------------------------------------------------------

BEGIN;

-- 1. 인벤토리에 아이템 추가 (또는 수량 증가)
INSERT INTO player_inventory (player_id, item_id, quantity)
VALUES ('player_uuid', 5, 1)
ON CONFLICT (player_id, item_id)
DO UPDATE SET quantity = player_inventory.quantity + 1;

-- 2. Turn 증가
SELECT advance_turn('session_uuid');

-- 3. Turn 상태 변경 기록
SELECT update_turn_state_changes(
    'session_uuid',
    (SELECT current_turn FROM session WHERE session_id = 'session_uuid'),
    '{"inventory_added": [5], "quantity": 1}'::jsonb,
    'item_acquisition'
);

COMMIT;


-- --------------------------------------------------------------------
-- 9-3. Phase 전환 + Turn 증가 (전투 시작)
-- 용도: 탐색 중 전투 돌입
-- --------------------------------------------------------------------

BEGIN;

-- 1. Phase 변경 (exploration → combat)
SELECT change_phase('session_uuid', 'combat'::phase_type);

-- 2. 적 생성
INSERT INTO enemy (session_id, enemy_id, name, hp, max_hp)
VALUES ('session_uuid', 1, 'Goblin', 30, 30);

-- 3. Turn 증가 (Phase 전환 자체도 상태 변경)
SELECT advance_turn('session_uuid');

-- 4. Turn 상태 변경 기록
SELECT update_turn_state_changes(
    'session_uuid',
    (SELECT current_turn FROM session WHERE session_id = 'session_uuid'),
    '{"phase_changed": "combat", "enemy_spawned": "Goblin"}'::jsonb,
    'phase_transition'
);

COMMIT;


-- ####################################################################
-- [작업영역 10] 디버깅 및 분석 쿼리
-- ####################################################################

-- --------------------------------------------------------------------
-- 10-1. Session 전체 상태 덤프 (디버깅용)
-- 용도: 문제 발생 시 전체 상태 확인
-- --------------------------------------------------------------------

-- Session 기본 정보
SELECT * FROM session WHERE session_id = $1;

-- 연결된 Player
SELECT * FROM player WHERE session_id = $1;

-- Inventory
SELECT pi.*, p.player_id
FROM player_inventory pi
JOIN player p ON pi.player_id = p.player_id
WHERE p.session_id = $1;

-- NPC Relations
SELECT pnr.*, p.player_id
FROM player_npc_relations pnr
JOIN player p ON pnr.player_id = p.player_id
WHERE p.session_id = $1;

-- NPC Instances
SELECT * FROM npc WHERE session_id = $1;

-- Enemy Instances
SELECT * FROM enemy WHERE session_id = $1 AND is_defeated = false;

-- Phase History
SELECT * FROM phase_history WHERE session_id = $1 ORDER BY transitioned_at;

-- Turn History
SELECT * FROM turn_history WHERE session_id = $1 ORDER BY turn_number;


-- --------------------------------------------------------------------
-- 10-2. 느린 쿼리 분석
-- 용도: 성능 최적화
-- --------------------------------------------------------------------

-- Turn 증가 속도 분석
SELECT
    turn_number,
    created_at,
    created_at - LAG(created_at) OVER (ORDER BY turn_number) AS turn_duration
FROM turn_history
WHERE session_id = $1
ORDER BY turn_number;


-- --------------------------------------------------------------------
-- 10-3. Session별 데이터 정리 (테스트/개발용)
-- 용도: 특정 세션의 모든 데이터 삭제
-- ⚠️ 주의: CASCADE 삭제되므로 프로덕션에서는 신중히 사용
-- --------------------------------------------------------------------

-- 특정 세션 완전 삭제
DELETE FROM session WHERE session_id = $1;
-- 연결된 player, inventory, npc, enemy 등도 CASCADE로 자동 삭제됨


-- ####################################################################
-- [작업영역 11] 유틸리티 쿼리
-- ####################################################################

-- --------------------------------------------------------------------
-- 11-1. 테스트 데이터 생성
-- 용도: 개발/테스트 환경에서 샘플 데이터 생성
-- --------------------------------------------------------------------

-- 테스트 세션 생성
DO $$
DECLARE
    test_scenario_id UUID := '550e8400-e29b-41d4-a716-446655440000';
    test_session_id UUID;
BEGIN
    -- Session 생성
    test_session_id := create_session(test_scenario_id, 1, 1, 'Test Town');

    RAISE NOTICE 'Test session created: %', test_session_id;

    -- Phase 전환 테스트
    PERFORM change_phase(test_session_id, 'exploration'::phase_type);
    PERFORM advance_turn(test_session_id);

    PERFORM change_phase(test_session_id, 'combat'::phase_type);
    PERFORM advance_turn(test_session_id);

    RAISE NOTICE 'Test data created successfully';
END $$;


-- --------------------------------------------------------------------
-- 11-2. 모든 활성 세션 일괄 일시정지
-- 용도: 서버 점검 전 모든 게임 세이브
-- --------------------------------------------------------------------

UPDATE session
SET status = 'paused',
    paused_at = NOW()
WHERE status = 'active';


-- --------------------------------------------------------------------
-- 11-3. 오래된 종료 세션 정리
-- 용도: 디스크 공간 확보
-- --------------------------------------------------------------------

-- 30일 이상 지난 종료 세션 삭제
DELETE FROM session
WHERE status = 'ended'
  AND ended_at < NOW() - INTERVAL '30 days';


-- ====================================================================
-- 파일 끝
-- ====================================================================
