-- ====================================================================
-- turn_history_dml.sql
-- Turn History 관련 모든 DML 쿼리 통합 파일
-- 작업영역별로 주석으로 구분되어 있음
-- ====================================================================


-- ####################################################################
-- [작업영역 1] TURN HISTORY 조회
-- ####################################################################

-- --------------------------------------------------------------------
-- 1-1. 특정 세션의 Turn 이력 조회 (전체)
-- 용도: 게임 진행 중 Turn별 상태 변경 확인
-- API: GET /state/session/{session_id}/turn-history
-- --------------------------------------------------------------------

SELECT * FROM get_turn_history($1);  -- session_id

-- 또는 직접 쿼리
SELECT
    history_id,
    session_id,
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    related_entities,
    created_at
FROM turn_history
WHERE session_id = $1
ORDER BY turn_number ASC;

-- 결과 예:
-- turn_number | phase_at_turn | turn_type      | state_changes                      | created_at
-- ------------|---------------|----------------|------------------------------------|------------------
-- 1           | dialogue      | state_change   | {"player_hp": -10}                 | 2026-01-23 10:05
-- 2           | dialogue      | state_change   | {"gold": 50}                       | 2026-01-23 10:08
-- 3           | combat        | phase_transition | {"phase_changed": "combat"}      | 2026-01-23 10:15
-- 4           | combat        | combat_action  | {"player_hp": -15, "enemy_hp": -20}| 2026-01-23 10:16


-- --------------------------------------------------------------------
-- 1-2. 최근 N개의 Turn 조회
-- 용도: UI에 최근 Turn 기록 표시
-- API: GET /state/session/{session_id}/turn-history?limit=10
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
ORDER BY turn_number DESC
LIMIT $2;  -- limit (예: 10)


-- --------------------------------------------------------------------
-- 1-3. 특정 Turn의 상세 정보 조회
-- 용도: "Turn 5에서 무슨 일이 있었나"
-- API: GET /state/session/{session_id}/turns/{turn_number}
-- --------------------------------------------------------------------

SELECT * FROM get_turn_details($1, $2);  -- session_id, turn_number

-- 또는 직접 쿼리
SELECT
    history_id,
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    related_entities,
    created_at
FROM turn_history
WHERE session_id = $1
  AND turn_number = $2;


-- --------------------------------------------------------------------
-- 1-4. Turn 범위 조회 (리플레이용)
-- 용도: "Turn 1~10까지의 진행 내용"
-- API: GET /state/session/{session_id}/turns?start=1&end=10
-- --------------------------------------------------------------------

SELECT * FROM get_turn_range($1, $2, $3);  -- session_id, start_turn, end_turn

-- 또는 직접 쿼리
SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
  AND turn_number BETWEEN $2 AND $3
ORDER BY turn_number ASC;


-- --------------------------------------------------------------------
-- 1-5. 가장 최근 Turn 조회
-- 용도: "마지막 Turn에서 어떤 변경이 있었나"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
ORDER BY turn_number DESC
LIMIT 1;


-- ####################################################################
-- [작업영역 2] TURN 상태 변경 기록 업데이트
-- ####################################################################

-- --------------------------------------------------------------------
-- 2-1. Turn 상태 변경 내용 업데이트
-- 용도: Turn 진행 후 state_changes 기록
-- 트리거가 빈 객체로 생성하므로, 이후 업데이트 필요
-- --------------------------------------------------------------------

-- 함수 사용
SELECT update_turn_state_changes(
    'session_uuid'::UUID,                                    -- session_id
    5,                                                        -- turn_number
    '{"player_hp": -10, "enemy_hp": -20, "gold": 50}'::jsonb, -- state_changes
    'combat_action'                                           -- turn_type
);

-- 또는 직접 UPDATE
UPDATE turn_history
SET
    state_changes = $2,  -- JSONB
    turn_type = $3       -- VARCHAR
WHERE session_id = $1
  AND turn_number = (
      SELECT current_turn
      FROM session
      WHERE session_id = $1
  );


-- --------------------------------------------------------------------
-- 2-2. Turn type만 업데이트
-- 용도: Turn 유형 분류
-- --------------------------------------------------------------------

UPDATE turn_history
SET turn_type = $3  -- 예: 'gm_commit', 'phase_transition', 'item_acquisition'
WHERE session_id = $1
  AND turn_number = $2;


-- --------------------------------------------------------------------
-- 2-3. 상태 변경 내용 추가 (병합)
-- 용도: 기존 state_changes에 새 변경 사항 추가
-- --------------------------------------------------------------------

-- JSONB 병합 (||= 연산자)
UPDATE turn_history
SET state_changes = state_changes || $3::jsonb
WHERE session_id = $1
  AND turn_number = $2;

-- 예: 기존 {"player_hp": -10}에 {"gold": 50} 추가
-- → 결과: {"player_hp": -10, "gold": 50}


-- --------------------------------------------------------------------
-- 2-4. 관련 엔티티 기록
-- 용도: 어떤 player, npc, enemy가 영향받았는지 기록
-- --------------------------------------------------------------------

UPDATE turn_history
SET related_entities = $3  -- UUID[] 예: ARRAY['player_uuid', 'enemy_uuid']
WHERE session_id = $1
  AND turn_number = $2;


-- ####################################################################
-- [작업영역 3] PHASE별 TURN 분석
-- ####################################################################

-- --------------------------------------------------------------------
-- 3-1. Phase별 Turn 수 집계
-- 용도: "각 Phase에서 몇 개의 Turn이 진행됐나"
-- API: GET /state/session/{session_id}/turns-per-phase
-- --------------------------------------------------------------------

SELECT * FROM get_turns_per_phase($1);  -- session_id

-- 결과 예:
-- phase       | turn_count
-- ------------|------------
-- combat      | 15
-- exploration | 8
-- dialogue    | 3


-- --------------------------------------------------------------------
-- 3-2. 특정 Phase의 Turn만 조회
-- 용도: "combat Phase에서의 Turn만 보기"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
  AND phase_at_turn = $2  -- 예: 'combat'::phase_type
ORDER BY turn_number ASC;


-- --------------------------------------------------------------------
-- 3-3. Phase별 평균 Turn 수
-- 용도: "평균적으로 각 Phase에서 몇 개의 Turn이 진행되나"
-- --------------------------------------------------------------------

WITH phase_sessions AS (
    SELECT
        phase_at_turn,
        COUNT(*) AS turn_count
    FROM turn_history
    WHERE session_id = $1
    GROUP BY phase_at_turn
)
SELECT
    phase_at_turn AS phase,
    turn_count,
    turn_count::float / NULLIF(
        (SELECT COUNT(DISTINCT new_phase)
         FROM phase_history
         WHERE session_id = $1), 0
    ) AS avg_turns_per_phase_visit
FROM phase_sessions
ORDER BY turn_count DESC;


-- ####################################################################
-- [작업영역 4] TURN TYPE별 분석
-- ####################################################################

-- --------------------------------------------------------------------
-- 4-1. Turn Type별 집계
-- 용도: "어떤 종류의 Turn이 많았나"
-- --------------------------------------------------------------------

SELECT
    turn_type,
    COUNT(*) AS count,
    ROUND(COUNT(*)::numeric / (
        SELECT COUNT(*) FROM turn_history WHERE session_id = $1
    ) * 100, 2) AS percentage
FROM turn_history
WHERE session_id = $1
GROUP BY turn_type
ORDER BY count DESC;

-- 결과 예:
-- turn_type       | count | percentage
-- ----------------|-------|------------
-- combat_action   | 15    | 50.00
-- state_change    | 10    | 33.33
-- phase_transition| 3     | 10.00
-- gm_commit       | 2     | 6.67


-- --------------------------------------------------------------------
-- 4-2. 특정 Type의 Turn만 조회
-- 용도: "combat_action Turn만 보기"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
  AND turn_type = $2  -- 예: 'combat_action'
ORDER BY turn_number ASC;


-- --------------------------------------------------------------------
-- 4-3. Type이 지정되지 않은 Turn 찾기
-- 용도: "기본값 'auto'로 남아있는 Turn"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
  AND turn_type = 'auto'
ORDER BY turn_number DESC;


-- ####################################################################
-- [작업영역 5] STATE CHANGES 분석
-- ####################################################################

-- --------------------------------------------------------------------
-- 5-1. 특정 키를 포함한 상태 변경 검색
-- 용도: "player_hp가 변경된 Turn 찾기"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
  AND state_changes ? $2  -- JSONB ? 연산자 (키 존재 확인)
ORDER BY turn_number ASC;

-- 예: state_changes ? 'player_hp'


-- --------------------------------------------------------------------
-- 5-2. 특정 값이 변경된 Turn 검색
-- 용도: "gold가 증가한 Turn만"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    state_changes,
    (state_changes->>'gold')::int AS gold_change,
    created_at
FROM turn_history
WHERE session_id = $1
  AND state_changes ? 'gold'
  AND (state_changes->>'gold')::int > 0
ORDER BY turn_number ASC;


-- --------------------------------------------------------------------
-- 5-3. 여러 키가 동시에 변경된 Turn
-- 용도: "HP와 골드가 동시에 변한 Turn"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
  AND state_changes ?& ARRAY['player_hp', 'gold']  -- 모든 키 포함
ORDER BY turn_number ASC;


-- --------------------------------------------------------------------
-- 5-4. 상태 변경이 비어있는 Turn 찾기
-- 용도: "아무 변경도 없는 Turn (데이터 무결성 확인)"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    created_at
FROM turn_history
WHERE session_id = $1
  AND (state_changes = '{}'::jsonb OR state_changes IS NULL)
ORDER BY turn_number ASC;


-- --------------------------------------------------------------------
-- 5-5. 특정 상태 변경 값 추출
-- 용도: "각 Turn에서 player_hp 변화량만 추출"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    state_changes->>'player_hp' AS player_hp_change,
    state_changes->>'enemy_hp' AS enemy_hp_change,
    created_at
FROM turn_history
WHERE session_id = $1
  AND state_changes ? 'player_hp'
ORDER BY turn_number ASC;


-- ####################################################################
-- [작업영역 6] TURN 소요 시간 분석
-- ####################################################################

-- --------------------------------------------------------------------
-- 6-1. 평균 Turn 소요 시간
-- 용도: "Turn당 평균 몇 분 걸렸나"
-- API: GET /state/session/{session_id}/average-turn-duration
-- --------------------------------------------------------------------

SELECT get_average_turn_duration($1);  -- session_id

-- 결과 예: 00:02:30 (2분 30초)


-- --------------------------------------------------------------------
-- 6-2. 각 Turn의 소요 시간 계산
-- 용도: "Turn별로 얼마나 걸렸나"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    created_at,
    created_at - LAG(created_at) OVER (ORDER BY turn_number) AS turn_duration
FROM turn_history
WHERE session_id = $1
ORDER BY turn_number ASC;


-- --------------------------------------------------------------------
-- 6-3. 가장 오래 걸린 Turn 찾기
-- 용도: "어느 Turn이 가장 오래 걸렸나"
-- --------------------------------------------------------------------

WITH turn_durations AS (
    SELECT
        turn_number,
        phase_at_turn,
        turn_type,
        created_at - LAG(created_at) OVER (ORDER BY turn_number) AS duration
    FROM turn_history
    WHERE session_id = $1
)
SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    duration
FROM turn_durations
WHERE duration IS NOT NULL
ORDER BY duration DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- 6-4. 가장 빠르게 진행된 Turn 찾기
-- 용도: "너무 빨리 끝난 Turn (봇/매크로 탐지)"
-- --------------------------------------------------------------------

WITH turn_durations AS (
    SELECT
        turn_number,
        phase_at_turn,
        turn_type,
        created_at - LAG(created_at) OVER (ORDER BY turn_number) AS duration
    FROM turn_history
    WHERE session_id = $1
)
SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    duration
FROM turn_durations
WHERE duration IS NOT NULL
  AND duration < INTERVAL '5 seconds'
ORDER BY duration ASC;


-- --------------------------------------------------------------------
-- 6-5. Phase별 평균 Turn 소요 시간
-- 용도: "각 Phase에서 Turn당 평균 몇 분 걸리나"
-- --------------------------------------------------------------------

WITH turn_durations AS (
    SELECT
        turn_number,
        phase_at_turn,
        created_at - LAG(created_at) OVER (ORDER BY turn_number) AS duration
    FROM turn_history
    WHERE session_id = $1
)
SELECT
    phase_at_turn AS phase,
    COUNT(*) AS turn_count,
    AVG(duration) AS avg_duration,
    MIN(duration) AS min_duration,
    MAX(duration) AS max_duration
FROM turn_durations
WHERE duration IS NOT NULL
GROUP BY phase_at_turn
ORDER BY avg_duration DESC;


-- ####################################################################
-- [작업영역 7] 복합 쿼리 (다른 테이블과 조인)
-- ####################################################################

-- --------------------------------------------------------------------
-- 7-1. Turn + Phase History 조인
-- 용도: "Turn과 Phase 전환을 함께 보기"
-- --------------------------------------------------------------------

SELECT
    th.turn_number,
    th.phase_at_turn,
    th.turn_type,
    th.state_changes,
    ph.previous_phase,
    ph.new_phase,
    ph.transition_reason,
    th.created_at
FROM turn_history th
LEFT JOIN phase_history ph
    ON th.session_id = ph.session_id
    AND th.turn_number = ph.turn_at_transition
WHERE th.session_id = $1
ORDER BY th.turn_number ASC;


-- --------------------------------------------------------------------
-- 7-2. Turn + Session 조인
-- 용도: "Session 정보와 함께 Turn 이력 확인"
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.scenario_id,
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


-- --------------------------------------------------------------------
-- 7-3. Turn + Player 상태 추적
-- 용도: "각 Turn에서 Player 상태가 어떻게 변했나"
-- (개념적 쿼리 - 실제로는 state_changes에서 추출)
-- --------------------------------------------------------------------

SELECT
    th.turn_number,
    th.phase_at_turn,
    th.state_changes->>'player_hp' AS hp_change,
    th.state_changes->>'gold' AS gold_change,
    th.state_changes->>'inventory_added' AS items_added,
    th.created_at
FROM turn_history th
WHERE th.session_id = $1
ORDER BY th.turn_number ASC;


-- ####################################################################
-- [작업영역 8] 리플레이 및 상태 복원
-- ####################################################################

-- --------------------------------------------------------------------
-- 8-1. 특정 Turn까지의 상태 변경 집계 (리플레이)
-- 용도: "Turn 10까지의 누적 변경 사항"
-- API: GET /state/session/{session_id}/replay/{turn_number}
-- --------------------------------------------------------------------

SELECT replay_to_turn($1, $2);  -- session_id, target_turn

-- 결과: JSONB 배열
-- [
--   {"turn": 1, "phase": "dialogue", "changes": {"player_hp": -10}},
--   {"turn": 2, "phase": "dialogue", "changes": {"gold": 50}},
--   ...
-- ]


-- --------------------------------------------------------------------
-- 8-2. Turn별 누적 상태 계산 (HP 예시)
-- 용도: "각 Turn 후 총 HP가 얼마였나"
-- --------------------------------------------------------------------

WITH hp_changes AS (
    SELECT
        turn_number,
        (state_changes->>'player_hp')::int AS hp_change
    FROM turn_history
    WHERE session_id = $1
      AND state_changes ? 'player_hp'
    ORDER BY turn_number
)
SELECT
    turn_number,
    hp_change,
    SUM(hp_change) OVER (ORDER BY turn_number) AS cumulative_hp_change
FROM hp_changes;


-- --------------------------------------------------------------------
-- 8-3. 특정 시점의 전체 상태 스냅샷 재구성
-- 용도: "Turn 5 시점의 전체 상태 복원"
-- --------------------------------------------------------------------

SELECT jsonb_object_agg(
    key,
    value
) AS state_at_turn
FROM (
    SELECT DISTINCT ON (key)
        key,
        value
    FROM turn_history,
    LATERAL jsonb_each(state_changes)
    WHERE session_id = $1
      AND turn_number <= $2  -- target_turn
    ORDER BY key, turn_number DESC
) latest_changes;


-- ####################################################################
-- [작업영역 9] 디버깅 및 이상 탐지
-- ####################################################################

-- --------------------------------------------------------------------
-- 9-1. Turn 번호 연속성 확인
-- 용도: "누락된 Turn이 있나"
-- --------------------------------------------------------------------

WITH expected_turns AS (
    SELECT generate_series(
        1,
        (SELECT MAX(turn_number) FROM turn_history WHERE session_id = $1)
    ) AS expected_turn
)
SELECT expected_turn
FROM expected_turns
WHERE expected_turn NOT IN (
    SELECT turn_number
    FROM turn_history
    WHERE session_id = $1
)
ORDER BY expected_turn;


-- --------------------------------------------------------------------
-- 9-2. 중복된 Turn 번호 찾기
-- 용도: "같은 Turn이 여러 번 기록됐나 (오류)"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    COUNT(*) AS duplicate_count
FROM turn_history
WHERE session_id = $1
GROUP BY turn_number
HAVING COUNT(*) > 1
ORDER BY turn_number;


-- --------------------------------------------------------------------
-- 9-3. Phase와 Turn의 불일치 찾기
-- 용도: "Turn의 phase_at_turn이 실제 Phase와 다른 경우"
-- --------------------------------------------------------------------

SELECT
    th.turn_number,
    th.phase_at_turn AS recorded_phase,
    ph.new_phase AS actual_phase,
    th.created_at
FROM turn_history th
LEFT JOIN phase_history ph
    ON th.session_id = ph.session_id
    AND th.turn_number >= ph.turn_at_transition
WHERE th.session_id = $1
  AND th.phase_at_turn != ph.new_phase
ORDER BY th.turn_number;


-- --------------------------------------------------------------------
-- 9-4. 비정상적으로 큰 상태 변경 찾기
-- 용도: "HP가 한 번에 -100 이상 변한 Turn"
-- --------------------------------------------------------------------

SELECT
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes->>'player_hp' AS hp_change,
    state_changes,
    created_at
FROM turn_history
WHERE session_id = $1
  AND state_changes ? 'player_hp'
  AND ABS((state_changes->>'player_hp')::int) > 100
ORDER BY turn_number ASC;


-- ####################################################################
-- [작업영역 10] 데이터 관리 (삭제/정리)
-- ####################################################################

-- --------------------------------------------------------------------
-- 10-1. 특정 세션의 Turn 이력 전체 삭제
-- 용도: 테스트 데이터 정리
-- ⚠️ 주의: 히스토리 데이터 영구 삭제
-- --------------------------------------------------------------------

DELETE FROM turn_history
WHERE session_id = $1;


-- --------------------------------------------------------------------
-- 10-2. 특정 Turn 이후 데이터 삭제
-- 용도: "Turn 10 이후를 되돌리기 (rollback)"
-- --------------------------------------------------------------------

DELETE FROM turn_history
WHERE session_id = $1
  AND turn_number > $2;  -- rollback_turn


-- --------------------------------------------------------------------
-- 10-3. 특정 Turn만 삭제
-- 용도: 잘못 기록된 특정 Turn 제거
-- --------------------------------------------------------------------

DELETE FROM turn_history
WHERE session_id = $1
  AND turn_number = $2;


-- --------------------------------------------------------------------
-- 10-4. 오래된 Turn 이력 정리 (보관 기간 초과)
-- 용도: 디스크 공간 확보
-- --------------------------------------------------------------------

-- 90일 이상 지난 종료 세션의 Turn 이력 삭제
DELETE FROM turn_history
WHERE session_id IN (
    SELECT session_id
    FROM session
    WHERE status = 'ended'
      AND ended_at < NOW() - INTERVAL '90 days'
);


-- ####################################################################
-- [작업영역 11] 리포트 생성 (분석/통계)
-- ####################################################################

-- --------------------------------------------------------------------
-- 11-1. Turn 요약 리포트
-- 용도: 세션 종료 후 플레이 리뷰
-- --------------------------------------------------------------------

SELECT
    COUNT(*) AS total_turns,
    COUNT(DISTINCT phase_at_turn) AS phases_used,
    COUNT(DISTINCT turn_type) AS turn_types_used,
    MIN(created_at) AS first_turn_at,
    MAX(created_at) AS last_turn_at,
    MAX(created_at) - MIN(created_at) AS total_session_duration,
    (MAX(created_at) - MIN(created_at)) / NULLIF(COUNT(*), 0) AS avg_turn_duration
FROM turn_history
WHERE session_id = $1;


-- --------------------------------------------------------------------
-- 11-2. 상태 변경 빈도 분석
-- 용도: "어떤 상태가 가장 자주 변경됐나"
-- --------------------------------------------------------------------

SELECT
    key AS state_key,
    COUNT(*) AS change_count,
    ROUND(COUNT(*)::numeric / (
        SELECT COUNT(*) FROM turn_history WHERE session_id = $1
    ) * 100, 2) AS percentage
FROM turn_history,
LATERAL jsonb_each(state_changes)
WHERE session_id = $1
GROUP BY key
ORDER BY change_count DESC;


-- --------------------------------------------------------------------
-- 11-3. Turn 타임라인 (JSON 형식)
-- 용도: 프론트엔드 타임라인 UI
-- --------------------------------------------------------------------

SELECT jsonb_agg(
    jsonb_build_object(
        'turn', turn_number,
        'phase', phase_at_turn,
        'type', turn_type,
        'changes', state_changes,
        'timestamp', created_at
    ) ORDER BY turn_number
) AS turn_timeline
FROM turn_history
WHERE session_id = $1;


-- --------------------------------------------------------------------
-- 11-4. Phase별 Turn 분포 히트맵
-- 용도: 시각화 대시보드
-- --------------------------------------------------------------------

SELECT
    DATE(created_at) AS date,
    EXTRACT(HOUR FROM created_at) AS hour,
    phase_at_turn,
    COUNT(*) AS turn_count
FROM turn_history
WHERE session_id = $1
GROUP BY date, hour, phase_at_turn
ORDER BY date, hour, phase_at_turn;


-- ####################################################################
-- [작업영역 12] 테스트 및 유틸리티
-- ####################################################################

-- --------------------------------------------------------------------
-- 12-1. Turn 이력 전체 덤프 (디버깅용)
-- 용도: 문제 발생 시 전체 이력 확인
-- --------------------------------------------------------------------

SELECT
    history_id,
    session_id,
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    related_entities,
    created_at
FROM turn_history
WHERE session_id = $1
ORDER BY turn_number ASC;


-- --------------------------------------------------------------------
-- 12-2. Turn 테스트 데이터 생성
-- 용도: 개발/테스트 환경
-- --------------------------------------------------------------------

-- 수동으로 Turn 이력 삽입 (트리거 우회)
INSERT INTO turn_history (
    session_id,
    turn_number,
    phase_at_turn,
    turn_type,
    state_changes,
    created_at
)
VALUES
    ($1, 1, 'dialogue', 'state_change', '{"player_hp": -10}'::jsonb, NOW() - INTERVAL '1 hour'),
    ($1, 2, 'dialogue', 'state_change', '{"gold": 50}'::jsonb, NOW() - INTERVAL '55 minutes'),
    ($1, 3, 'combat', 'phase_transition', '{"phase_changed": "combat"}'::jsonb, NOW() - INTERVAL '50 minutes'),
    ($1, 4, 'combat', 'combat_action', '{"player_hp": -15, "enemy_hp": -20}'::jsonb, NOW() - INTERVAL '45 minutes'),
    ($1, 5, 'combat', 'combat_action', '{"player_hp": -5, "enemy_hp": -25}'::jsonb, NOW() - INTERVAL '40 minutes');


-- --------------------------------------------------------------------
-- 12-3. Turn 이력 존재 여부 확인
-- 용도: 테스트 검증
-- --------------------------------------------------------------------

SELECT EXISTS(
    SELECT 1
    FROM turn_history
    WHERE session_id = $1
) AS has_turn_history;


-- --------------------------------------------------------------------
-- 12-4. 세션별 Turn 이력 카운트
-- 용도: 데이터 무결성 확인
-- --------------------------------------------------------------------

SELECT
    session_id,
    COUNT(*) AS turn_count,
    MIN(turn_number) AS first_turn,
    MAX(turn_number) AS last_turn,
    MIN(created_at) AS first_turn_at,
    MAX(created_at) AS last_turn_at
FROM turn_history
GROUP BY session_id
ORDER BY turn_count DESC;


-- --------------------------------------------------------------------
-- 12-5. Turn과 Session의 current_turn 일치 확인
-- 용도: 데이터 무결성 검증
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.current_turn AS session_current_turn,
    MAX(th.turn_number) AS max_turn_in_history,
    CASE
        WHEN s.current_turn = MAX(th.turn_number) THEN 'OK'
        ELSE 'MISMATCH'
    END AS status
FROM session s
LEFT JOIN turn_history th ON s.session_id = th.session_id
WHERE s.status = 'active'
GROUP BY s.session_id, s.current_turn
ORDER BY status DESC, s.session_id;


-- ====================================================================
-- 파일 끝
-- ====================================================================
