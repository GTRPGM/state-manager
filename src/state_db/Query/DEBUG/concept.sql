
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



-- ####################################################################
-- [작업영역 3] ACT + SEQUENCE 통합 관리
-- ####################################################################

-- --------------------------------------------------------------------
-- 3-1. Act와 Sequence를 동시에 지정
-- 용도: 특정 지점으로 바로 이동 (시나리오 테스트, GM 명령)
-- API: PUT /state/session/{session_id}/progress
-- --------------------------------------------------------------------

SELECT update_act_sequence(
    $1,  -- session_id
    $2,  -- new_act (예: 2)
    $3   -- new_sequence (예: 3)
);

-- 또는 직접 쿼리
UPDATE session
SET
    current_act = $2,      -- new_act
    current_sequence = $3  -- new_sequence
WHERE session_id = $1
  AND status = 'active'
RETURNING current_act, current_sequence;

-- 결과 예: (2, 3) - Act 2, Sequence 3


-- --------------------------------------------------------------------
-- 3-2. 현재 Act/Sequence 조회 (통합)
-- 용도: UI 표시, 진행 상황 확인
-- API: GET /state/session/{session_id}/progress
-- --------------------------------------------------------------------

SELECT
    current_act,
    current_sequence,
    -- 진행률 계산 (예시: Act당 10개 Sequence 가정)
    ROUND(((current_act - 1) * 10 + current_sequence)::numeric /
          (3 * 10) * 100, 2) AS progress_percentage  -- 총 3개 Act 가정
FROM session
WHERE session_id = $1;

-- 결과 예: (2, 5, 50.00) - Act 2, Sequence 5, 진행률 50%


-- --------------------------------------------------------------------
-- 3-3. Act/Sequence를 문자열로 포맷
-- 용도: UI 표시용 포맷팅
-- --------------------------------------------------------------------

SELECT
    session_id,
    CONCAT('Act ', current_act, ' - Seq ', current_sequence) AS progress_display,
    CONCAT(current_act, '-', current_sequence) AS progress_code
FROM session
WHERE session_id = $1;

-- 결과 예:
-- progress_display: "Act 2 - Seq 3"
-- progress_code: "2-3"


-- ####################################################################
-- [작업영역 4] ACT/SEQUENCE 진행 조건 검증
-- ####################################################################

-- --------------------------------------------------------------------
-- 4-1. Sequence 완료 조건 확인
-- 용도: "현재 Sequence를 완료했는가" 검증
-- 예: 특정 목표 달성, 모든 이벤트 완료 등
-- --------------------------------------------------------------------

-- 개념적 쿼리 (실제 조건은 비즈니스 로직에 따라 다름)
SELECT
    s.session_id,
    s.current_act,
    s.current_sequence,
    -- 예시: Turn이 10개 이상 진행되었으면 완료로 간주
    CASE
        WHEN s.current_turn >= 10 THEN true
        ELSE false
    END AS sequence_completed
FROM session s
WHERE s.session_id = $1;


-- --------------------------------------------------------------------
-- 4-2. Act 완료 조건 확인
-- 용도: "현재 Act를 완료했는가" 검증
-- 예: 모든 Sequence 완료, 보스 처치 등
-- --------------------------------------------------------------------

-- 개념적 쿼리
SELECT
    s.session_id,
    s.current_act,
    s.current_sequence,
    -- 예시: Sequence 5 이상이면 Act 완료로 간주
    CASE
        WHEN s.current_sequence >= 5 THEN true
        ELSE false
    END AS act_completed
FROM session s
WHERE s.session_id = $1;


-- --------------------------------------------------------------------
-- 4-3. 진행 가능 여부 종합 확인
-- 용도: UI에서 "다음으로" 버튼 활성화 여부 결정
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.current_act,
    s.current_sequence,
    s.current_turn,
    -- Sequence 진행 가능 여부
    CASE
        WHEN s.current_turn >= 5 THEN true  -- 예: Turn 5개 이상 진행 필요
        ELSE false
    END AS can_advance_sequence,
    -- Act 진행 가능 여부
    CASE
        WHEN s.current_sequence >= 5 THEN true  -- 예: Sequence 5까지 완료 필요
        ELSE false
    END AS can_advance_act
FROM session s
WHERE s.session_id = $1;


-- ####################################################################
-- [작업영역 5] ACT/SEQUENCE 이력 조회
-- ####################################################################

-- --------------------------------------------------------------------
-- 5-1. Act/Sequence 변경 이력 추적
-- 용도: "언제 어떤 Act/Sequence로 변경됐나"
-- ⚠️ 참고: session 테이블에는 이력이 없으므로 별도 로그 필요
-- (또는 Turn History의 state_changes에 기록)
-- --------------------------------------------------------------------

-- Turn History에서 Act/Sequence 변경 추출
SELECT
    turn_number,
    phase_at_turn,
    state_changes->>'current_act' AS new_act,
    state_changes->>'current_sequence' AS new_sequence,
    created_at
FROM turn_history
WHERE session_id = $1
  AND (state_changes ? 'current_act' OR state_changes ? 'current_sequence')
ORDER BY turn_number ASC;


-- --------------------------------------------------------------------
-- 5-2. 특정 Act에서 소요된 시간 계산
-- 용도: "Act 2에서 얼마나 걸렸나"
-- --------------------------------------------------------------------

-- 개념적 쿼리 (Act 변경 로그가 있다고 가정)
WITH act_changes AS (
    SELECT
        (state_changes->>'current_act')::int AS act_number,
        created_at
    FROM turn_history
    WHERE session_id = $1
      AND state_changes ? 'current_act'
    ORDER BY turn_number
)
SELECT
    act_number,
    created_at AS act_started_at,
    LEAD(created_at) OVER (ORDER BY created_at) - created_at AS act_duration
FROM act_changes;


-- --------------------------------------------------------------------
-- 5-3. 특정 Sequence에서 소요된 시간 계산
-- 용도: "Sequence 3에서 얼마나 걸렸나"
-- --------------------------------------------------------------------

-- 개념적 쿼리
WITH sequence_changes AS (
    SELECT
        (state_changes->>'current_act')::int AS act_number,
        (state_changes->>'current_sequence')::int AS sequence_number,
        created_at
    FROM turn_history
    WHERE session_id = $1
      AND state_changes ? 'current_sequence'
    ORDER BY turn_number
)
SELECT
    act_number,
    sequence_number,
    created_at AS sequence_started_at,
    LEAD(created_at) OVER (ORDER BY created_at) - created_at AS sequence_duration
FROM sequence_changes;


-- ####################################################################
-- [작업영역 6] ACT/SEQUENCE별 통계
-- ####################################################################

-- --------------------------------------------------------------------
-- 6-1. 현재 어느 Act에 있는 세션들 집계
-- 용도: 대시보드 - "각 Act별 진행 중인 세션 수"
-- --------------------------------------------------------------------

SELECT
    current_act,
    COUNT(*) AS session_count,
    AVG(current_sequence)::numeric(10,2) AS avg_sequence
FROM session
WHERE status = 'active'
GROUP BY current_act
ORDER BY current_act;

-- 결과 예:
-- current_act | session_count | avg_sequence
-- ------------|---------------|-------------
-- 1           | 5             | 2.40
-- 2           | 3             | 4.67
-- 3           | 1             | 1.00


-- --------------------------------------------------------------------
-- 6-2. 현재 어느 Sequence에 있는 세션들 집계
-- 용도: 대시보드 - "특정 Act 내 Sequence별 분포"
-- --------------------------------------------------------------------

SELECT
    current_act,
    current_sequence,
    COUNT(*) AS session_count
FROM session
WHERE status = 'active'
  AND current_act = $1  -- 특정 Act (예: 2)
GROUP BY current_act, current_sequence
ORDER BY current_sequence;


-- --------------------------------------------------------------------
-- 6-3. Act/Sequence별 평균 Turn 수
-- 용도: 밸런싱 분석 - "각 구간별 평균 Turn"
-- --------------------------------------------------------------------

-- 현재 진행 중인 세션 기준
SELECT
    current_act,
    current_sequence,
    AVG(current_turn)::numeric(10,2) AS avg_turns,
    MIN(current_turn) AS min_turns,
    MAX(current_turn) AS max_turns
FROM session
WHERE status = 'active'
GROUP BY current_act, current_sequence
ORDER BY current_act, current_sequence;


-- ####################################################################
-- [작업영역 7] ACT/SEQUENCE 기반 필터링
-- ####################################################################

-- --------------------------------------------------------------------
-- 7-1. 특정 Act에 있는 세션 조회
-- 용도: "Act 2에 있는 모든 세션"
-- --------------------------------------------------------------------

SELECT
    session_id,
    scenario_id,
    current_act,
    current_sequence,
    current_phase,
    current_turn,
    started_at
FROM session
WHERE current_act = $1  -- 예: 2
  AND status = 'active'
ORDER BY started_at DESC;


-- --------------------------------------------------------------------
-- 7-2. 특정 Act/Sequence에 있는 세션 조회
-- 용도: "Act 2, Sequence 3에 있는 세션"
-- --------------------------------------------------------------------

SELECT
    session_id,
    scenario_id,
    current_phase,
    current_turn,
    started_at
FROM session
WHERE current_act = $1        -- 예: 2
  AND current_sequence = $2   -- 예: 3
  AND status = 'active'
ORDER BY started_at DESC;


-- --------------------------------------------------------------------
-- 7-3. Act/Sequence 범위로 세션 조회
-- 용도: "Act 1-2 사이에 있는 세션"
-- --------------------------------------------------------------------

SELECT
    session_id,
    scenario_id,
    current_act,
    current_sequence,
    started_at
FROM session
WHERE current_act BETWEEN $1 AND $2  -- 예: 1, 2
  AND status = 'active'
ORDER BY current_act, current_sequence, started_at DESC;


-- --------------------------------------------------------------------
-- 7-4. 진행이 느린 세션 찾기
-- 용도: "Act 1에서 오래 머물러 있는 세션"
-- --------------------------------------------------------------------

SELECT
    session_id,
    scenario_id,
    current_act,
    current_sequence,
    current_turn,
    started_at,
    NOW() - started_at AS session_duration
FROM session
WHERE current_act = 1
  AND status = 'active'
  AND NOW() - started_at > INTERVAL '2 hours'  -- 2시간 이상
ORDER BY session_duration DESC;


-- ####################################################################
-- [작업영역 8] 복합 쿼리 (다른 개념과 조합)
-- ####################################################################

-- --------------------------------------------------------------------
-- 8-1. Act/Sequence + Phase 조합 분석
-- 용도: "각 Act에서 어떤 Phase를 많이 사용하나"
-- --------------------------------------------------------------------

SELECT
    s.current_act,
    s.current_sequence,
    th.phase_at_turn,
    COUNT(*) AS turn_count
FROM session s
JOIN turn_history th ON s.session_id = th.session_id
WHERE s.status = 'active'
GROUP BY s.current_act, s.current_sequence, th.phase_at_turn
ORDER BY s.current_act, s.current_sequence, turn_count DESC;


-- --------------------------------------------------------------------
-- 8-2. Act/Sequence별 평균 Phase 전환 횟수
-- 용도: "각 구간에서 Phase가 몇 번 바뀌나"
-- --------------------------------------------------------------------

SELECT
    s.current_act,
    s.current_sequence,
    COUNT(ph.history_id)::float / COUNT(DISTINCT s.session_id) AS avg_phase_transitions
FROM session s
LEFT JOIN phase_history ph ON s.session_id = ph.session_id
WHERE s.status = 'active'
GROUP BY s.current_act, s.current_sequence
ORDER BY s.current_act, s.current_sequence;


-- --------------------------------------------------------------------
-- 8-3. Act/Sequence별 평균 소요 시간
-- 용도: 밸런싱 - "각 구간별 평균 플레이 시간"
-- --------------------------------------------------------------------

-- 종료된 세션 기준
SELECT
    current_act,
    current_sequence,
    AVG(ended_at - started_at) AS avg_duration,
    COUNT(*) AS session_count
FROM session
WHERE status = 'ended'
GROUP BY current_act, current_sequence
ORDER BY current_act, current_sequence;


-- ####################################################################
-- [작업영역 9] 디버깅 및 데이터 무결성
-- ####################################################################

-- --------------------------------------------------------------------
-- 9-1. Act/Sequence가 유효 범위를 벗어난 세션 찾기
-- 용도: 데이터 무결성 확인
-- 예: Act는 1~3, Sequence는 1~10 범위
-- --------------------------------------------------------------------

SELECT
    session_id,
    scenario_id,
    current_act,
    current_sequence,
    status
FROM session
WHERE current_act NOT BETWEEN 1 AND 3
   OR current_sequence NOT BETWEEN 1 AND 10
ORDER BY session_id;


-- --------------------------------------------------------------------
-- 9-2. Act는 변경됐는데 Sequence가 1이 아닌 경우 찾기
-- 용도: 데이터 무결성 확인 (Act 변경 시 Sequence는 1이어야 함)
-- ⚠️ 참고: 직접 UPDATE한 경우 발생 가능
-- --------------------------------------------------------------------

-- 이력 로그에서 확인 (Turn History 사용)
WITH act_changes AS (
    SELECT
        session_id,
        turn_number,
        (state_changes->>'current_act')::int AS new_act,
        (state_changes->>'current_sequence')::int AS new_sequence
    FROM turn_history
    WHERE state_changes ? 'current_act'
      AND state_changes ? 'current_sequence'
)
SELECT *
FROM act_changes
WHERE new_sequence != 1
ORDER BY turn_number;


-- --------------------------------------------------------------------
-- 9-3. Act/Sequence 변경 없이 오래 진행된 세션
-- 용도: "같은 구간에서 너무 오래 머무른 세션"
-- --------------------------------------------------------------------

SELECT
    session_id,
    scenario_id,
    current_act,
    current_sequence,
    current_turn,
    NOW() - started_at AS session_duration
FROM session
WHERE status = 'active'
  AND current_turn > 50  -- Turn은 많이 진행됨
  AND current_act = 1    -- 하지만 Act 1에 머물러 있음
  AND current_sequence <= 2  -- Sequence도 낮음
ORDER BY session_duration DESC;


-- ####################################################################
-- [작업영역 10] 테스트 및 유틸리티
-- ####################################################################

-- --------------------------------------------------------------------
-- 10-1. Act/Sequence 초기화
-- 용도: 테스트 세션을 처음부터 다시 시작
-- --------------------------------------------------------------------

UPDATE session
SET
    current_act = 1,
    current_sequence = 1,
    current_turn = 0
WHERE session_id = $1;


-- --------------------------------------------------------------------
-- 10-2. Act/Sequence 범위 검증 함수 (선택적)
-- 용도: 업데이트 전 유효성 검증
-- --------------------------------------------------------------------

-- 개념적 함수 (DDL에 추가 필요)
/*
CREATE OR REPLACE FUNCTION validate_act_sequence(
    p_act INTEGER,
    p_sequence INTEGER
)
RETURNS BOOLEAN AS $$
BEGIN
    -- 예: Act는 1~3, Sequence는 1~10
    RETURN p_act BETWEEN 1 AND 3
       AND p_sequence BETWEEN 1 AND 10;
END;
$$ LANGUAGE plpgsql;
*/

-- 사용 예
SELECT validate_act_sequence(2, 5);  -- true
SELECT validate_act_sequence(4, 1);  -- false (Act 4는 존재하지 않음)


-- --------------------------------------------------------------------
-- 10-3. Act/Sequence 진행 시뮬레이션
-- 용도: 테스트 - 자동으로 진행 시뮬레이션
-- --------------------------------------------------------------------

DO $$
DECLARE
    test_session_id UUID := 'test-session-uuid';
BEGIN
    -- Sequence 증가
    PERFORM advance_sequence(test_session_id);
    RAISE NOTICE 'Sequence advanced';

    -- 5번 반복 후 Act 증가
    FOR i IN 1..5 LOOP
        PERFORM advance_sequence(test_session_id);
    END LOOP;

    PERFORM advance_act(test_session_id);
    RAISE NOTICE 'Act advanced';
END $$;


-- ====================================================================
-- 파일 끝
-- ====================================================================
