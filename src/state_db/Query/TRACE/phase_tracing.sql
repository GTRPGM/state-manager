-- ====================================================================
-- phase_history_dml.sql
-- Phase History 관련 모든 DML 쿼리 통합 파일
-- 작업영역별로 주석으로 구분되어 있음
-- ====================================================================


-- ####################################################################
-- [작업영역 1] PHASE HISTORY 조회
-- ####################################################################

-- --------------------------------------------------------------------
-- 1-1. 특정 세션의 Phase 전환 이력 조회 (전체)
-- 용도: 게임 진행 중 Phase 흐름 확인
-- API: GET /state/session/{session_id}/phase-history
-- --------------------------------------------------------------------

SELECT * FROM get_phase_history($1);  -- session_id

-- 또는 직접 쿼리
SELECT
    history_id,
    session_id,
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
ORDER BY transitioned_at ASC;

-- 결과 예:
-- previous_phase | new_phase   | turn_at_transition | transition_reason  | transitioned_at
-- ---------------|-------------|--------------------|--------------------|------------------
-- NULL           | dialogue    | 0                  | NULL               | 2026-01-23 10:00
-- dialogue       | exploration | 1                  | gm_command         | 2026-01-23 10:05
-- exploration    | combat      | 5                  | enemy_encounter    | 2026-01-23 10:15
-- combat         | exploration | 12                 | combat_ended       | 2026-01-23 10:30


-- --------------------------------------------------------------------
-- 1-2. 최근 N개의 Phase 전환 조회
-- 용도: UI에 최근 Phase 변경 이력 표시
-- API: GET /state/session/{session_id}/phase-history?limit=5
-- --------------------------------------------------------------------

SELECT
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
ORDER BY transitioned_at DESC
LIMIT $2;  -- limit (예: 5)


-- --------------------------------------------------------------------
-- 1-3. 특정 Phase로의 전환 이력만 조회
-- 용도: "언제 combat으로 전환했는지" 확인
-- API: GET /state/session/{session_id}/phase-history?phase=combat
-- --------------------------------------------------------------------

SELECT
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
  AND new_phase = $2  -- 예: 'combat'::phase_type
ORDER BY transitioned_at DESC;


-- --------------------------------------------------------------------
-- 1-4. 특정 Turn 범위의 Phase 전환 조회
-- 용도: "Turn 5~15 사이에 Phase가 몇 번 바뀌었나"
-- --------------------------------------------------------------------

SELECT
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
  AND turn_at_transition BETWEEN $2 AND $3  -- start_turn, end_turn
ORDER BY turn_at_transition ASC;


-- --------------------------------------------------------------------
-- 1-5. 가장 최근 Phase 전환 조회
-- 용도: "마지막으로 Phase가 바뀐 게 언제였지?"
-- --------------------------------------------------------------------

SELECT
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
ORDER BY transitioned_at DESC
LIMIT 1;


-- ####################################################################
-- [작업영역 2] PHASE 전환 원인(Reason) 업데이트
-- ####################################################################

-- --------------------------------------------------------------------
-- 2-1. 가장 최근 Phase 전환에 원인 추가
-- 용도: Phase 변경 후 원인을 기록
-- 트리거가 NULL로 생성하므로, 이후 업데이트 필요
-- --------------------------------------------------------------------

-- 가장 최근 기록 업데이트
UPDATE phase_history
SET transition_reason = $2  -- 예: 'enemy_encounter'
WHERE session_id = $1
  AND history_id = (
      SELECT history_id
      FROM phase_history
      WHERE session_id = $1
      ORDER BY transitioned_at DESC
      LIMIT 1
  );


-- --------------------------------------------------------------------
-- 2-2. 특정 history_id의 원인 업데이트
-- 용도: 특정 전환 이력에 원인 기록
-- --------------------------------------------------------------------

UPDATE phase_history
SET transition_reason = $2  -- 예: 'combat_victory'
WHERE history_id = $1;


-- --------------------------------------------------------------------
-- 2-3. 특정 Turn의 Phase 전환 원인 업데이트
-- 용도: Turn 번호로 Phase 전환 원인 기록
-- --------------------------------------------------------------------

UPDATE phase_history
SET transition_reason = $3  -- 예: 'story_progression'
WHERE session_id = $1
  AND turn_at_transition = $2;


-- ####################################################################
-- [작업영역 3] PHASE 지속 시간 및 통계
-- ####################################################################

-- --------------------------------------------------------------------
-- 3-1. 현재 Phase 지속 시간 조회
-- 용도: "현재 Phase가 시작된 지 얼마나 됐나"
-- API: GET /state/session/{session_id}/current-phase-duration
-- --------------------------------------------------------------------

SELECT get_current_phase_duration($1);  -- session_id

-- 결과 예: 00:15:30 (15분 30초)


-- --------------------------------------------------------------------
-- 3-2. Phase별 총 소요 시간 및 전환 횟수
-- 용도: 게임 밸런싱 분석
-- API: GET /state/session/{session_id}/phase-statistics
-- --------------------------------------------------------------------

SELECT * FROM get_phase_statistics($1);  -- session_id

-- 결과 예:
-- phase       | total_duration | transition_count
-- ------------|----------------|------------------
-- combat      | 01:20:00       | 3
-- exploration | 00:45:00       | 2
-- dialogue    | 00:30:00       | 1


-- --------------------------------------------------------------------
-- 3-3. 각 Phase별 평균 지속 시간 계산
-- 용도: "평균적으로 combat Phase는 얼마나 지속되나"
-- --------------------------------------------------------------------

WITH phase_durations AS (
    SELECT
        ph.new_phase,
        LEAD(ph.transitioned_at, 1, NOW()) OVER (ORDER BY ph.transitioned_at)
            - ph.transitioned_at AS duration
    FROM phase_history ph
    WHERE ph.session_id = $1
)
SELECT
    new_phase AS phase,
    AVG(duration) AS avg_duration,
    MIN(duration) AS min_duration,
    MAX(duration) AS max_duration,
    COUNT(*) AS occurrence_count
FROM phase_durations
GROUP BY new_phase
ORDER BY avg_duration DESC;


-- --------------------------------------------------------------------
-- 3-4. 시간대별 Phase 분포 (시각화용)
-- 용도: "오전/오후/저녁에 어떤 Phase가 많았나"
-- --------------------------------------------------------------------

SELECT
    EXTRACT(HOUR FROM transitioned_at) AS hour_of_day,
    new_phase,
    COUNT(*) AS transition_count
FROM phase_history
WHERE session_id = $1
GROUP BY hour_of_day, new_phase
ORDER BY hour_of_day, new_phase;


-- ####################################################################
-- [작업영역 4] PHASE 전환 패턴 분석
-- ####################################################################

-- --------------------------------------------------------------------
-- 4-1. Phase 전환 패턴 조회
-- 용도: "어떤 Phase에서 어떤 Phase로 자주 전환되나"
-- --------------------------------------------------------------------

SELECT
    previous_phase,
    new_phase,
    COUNT(*) AS transition_count
FROM phase_history
WHERE session_id = $1
  AND previous_phase IS NOT NULL
GROUP BY previous_phase, new_phase
ORDER BY transition_count DESC;

-- 결과 예:
-- previous_phase | new_phase   | transition_count
-- ---------------|-------------|------------------
-- exploration    | combat      | 5
-- combat         | exploration | 5
-- dialogue       | exploration | 2


-- --------------------------------------------------------------------
-- 4-2. 특정 Phase로 들어가는 전환 횟수
-- 용도: "combat으로 몇 번이나 전환됐나"
-- --------------------------------------------------------------------

SELECT
    new_phase,
    COUNT(*) AS entry_count
FROM phase_history
WHERE session_id = $1
  AND new_phase = $2  -- 예: 'combat'::phase_type
GROUP BY new_phase;


-- --------------------------------------------------------------------
-- 4-3. 특정 Phase에서 나가는 전환 횟수
-- 용도: "combat에서 몇 번이나 빠져나왔나"
-- --------------------------------------------------------------------

SELECT
    previous_phase,
    COUNT(*) AS exit_count
FROM phase_history
WHERE session_id = $1
  AND previous_phase = $2  -- 예: 'combat'::phase_type
GROUP BY previous_phase;


-- --------------------------------------------------------------------
-- 4-4. Phase 전환 시퀀스 조회 (연속된 전환)
-- 용도: "dialogue → exploration → combat 순서로 진행된 적이 있나"
-- --------------------------------------------------------------------

WITH phase_sequence AS (
    SELECT
        previous_phase,
        new_phase,
        LEAD(new_phase, 1) OVER (ORDER BY transitioned_at) AS next_phase,
        transitioned_at
    FROM phase_history
    WHERE session_id = $1
)
SELECT
    previous_phase,
    new_phase,
    next_phase,
    transitioned_at
FROM phase_sequence
WHERE previous_phase IS NOT NULL
  AND next_phase IS NOT NULL
ORDER BY transitioned_at;


-- ####################################################################
-- [작업영역 5] 특정 조건으로 PHASE 이력 필터링
-- ####################################################################

-- --------------------------------------------------------------------
-- 5-1. 특정 날짜 범위의 Phase 전환 조회
-- 용도: "어제 플레이한 내용 중 Phase 전환"
-- --------------------------------------------------------------------

SELECT
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
  AND transitioned_at BETWEEN $2 AND $3  -- start_date, end_date
ORDER BY transitioned_at ASC;


-- --------------------------------------------------------------------
-- 5-2. 특정 원인으로 발생한 Phase 전환만 조회
-- 용도: "enemy_encounter로 인한 combat 전환만 보기"
-- --------------------------------------------------------------------

SELECT
    previous_phase,
    new_phase,
    turn_at_transition,
    transitioned_at
FROM phase_history
WHERE session_id = $1
  AND transition_reason = $2  -- 예: 'enemy_encounter'
ORDER BY transitioned_at DESC;


-- --------------------------------------------------------------------
-- 5-3. 원인이 기록되지 않은 Phase 전환 조회
-- 용도: "원인을 기록하지 않은 전환 찾기"
-- --------------------------------------------------------------------

SELECT
    history_id,
    previous_phase,
    new_phase,
    turn_at_transition,
    transitioned_at
FROM phase_history
WHERE session_id = $1
  AND transition_reason IS NULL
ORDER BY transitioned_at DESC;


-- ####################################################################
-- [작업영역 6] 복합 쿼리 (다른 테이블과 조인)
-- ####################################################################

-- --------------------------------------------------------------------
-- 6-1. Phase 전환 + Session 정보 조인
-- 용도: Session 정보와 함께 Phase 이력 확인
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.scenario_id,
    s.current_phase,
    ph.previous_phase,
    ph.new_phase,
    ph.turn_at_transition,
    ph.transition_reason,
    ph.transitioned_at
FROM session s
LEFT JOIN phase_history ph ON s.session_id = ph.session_id
WHERE s.session_id = $1
ORDER BY ph.transitioned_at ASC;


-- --------------------------------------------------------------------
-- 6-2. Phase 전환 + Turn 정보 조인
-- 용도: "Phase 전환 시 어떤 상태 변경이 있었나"
-- --------------------------------------------------------------------

SELECT
    ph.previous_phase,
    ph.new_phase,
    ph.turn_at_transition,
    ph.transition_reason,
    th.turn_type,
    th.state_changes,
    ph.transitioned_at
FROM phase_history ph
LEFT JOIN turn_history th
    ON ph.session_id = th.session_id
    AND ph.turn_at_transition = th.turn_number
WHERE ph.session_id = $1
ORDER BY ph.transitioned_at ASC;


-- --------------------------------------------------------------------
-- 6-3. 여러 세션의 Phase 전환 비교
-- 용도: "같은 시나리오를 플레이한 세션들의 Phase 패턴 비교"
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.scenario_id,
    ph.new_phase,
    COUNT(*) AS transition_count,
    AVG(
        LEAD(ph.transitioned_at, 1, NOW()) OVER (
            PARTITION BY ph.session_id
            ORDER BY ph.transitioned_at
        ) - ph.transitioned_at
    ) AS avg_phase_duration
FROM session s
JOIN phase_history ph ON s.session_id = ph.session_id
WHERE s.scenario_id = $1  -- 특정 시나리오
GROUP BY s.session_id, s.scenario_id, ph.new_phase
ORDER BY s.session_id, transition_count DESC;


-- ####################################################################
-- [작업영역 7] 디버깅 및 이상 탐지
-- ####################################################################

-- --------------------------------------------------------------------
-- 7-1. 비정상적으로 짧은 Phase 지속 시간 찾기
-- 용도: "1분 미만으로 끝난 Phase 찾기"
-- --------------------------------------------------------------------

WITH phase_durations AS (
    SELECT
        history_id,
        session_id,
        new_phase,
        transitioned_at,
        LEAD(transitioned_at, 1, NOW()) OVER (ORDER BY transitioned_at)
            - transitioned_at AS duration
    FROM phase_history
    WHERE session_id = $1
)
SELECT
    history_id,
    new_phase,
    duration,
    transitioned_at
FROM phase_durations
WHERE duration < INTERVAL '1 minute'
ORDER BY duration ASC;


-- --------------------------------------------------------------------
-- 7-2. 비정상적으로 긴 Phase 지속 시간 찾기
-- 용도: "1시간 이상 지속된 Phase 찾기"
-- --------------------------------------------------------------------

WITH phase_durations AS (
    SELECT
        history_id,
        session_id,
        new_phase,
        transitioned_at,
        LEAD(transitioned_at, 1, NOW()) OVER (ORDER BY transitioned_at)
            - transitioned_at AS duration
    FROM phase_history
    WHERE session_id = $1
)
SELECT
    history_id,
    new_phase,
    duration,
    transitioned_at
FROM phase_durations
WHERE duration > INTERVAL '1 hour'
ORDER BY duration DESC;


-- --------------------------------------------------------------------
-- 7-3. 같은 Phase로의 연속 전환 찾기 (오류 가능성)
-- 용도: "exploration → exploration 같은 중복 전환"
-- --------------------------------------------------------------------

SELECT
    history_id,
    previous_phase,
    new_phase,
    turn_at_transition,
    transitioned_at
FROM phase_history
WHERE session_id = $1
  AND previous_phase = new_phase  -- 같은 Phase로 전환 (이상)
ORDER BY transitioned_at DESC;

-- ⚠️ 정상적으로는 CHECK 제약으로 방지되지만, 데이터 확인용


-- --------------------------------------------------------------------
-- 7-4. Phase 전환 없이 오래 지속된 세션 찾기
-- 용도: "Phase가 한 번도 안 바뀐 세션"
-- --------------------------------------------------------------------

SELECT
    s.session_id,
    s.current_phase,
    s.started_at,
    NOW() - s.started_at AS session_duration,
    COUNT(ph.history_id) AS phase_transition_count
FROM session s
LEFT JOIN phase_history ph ON s.session_id = ph.session_id
WHERE s.status = 'active'
GROUP BY s.session_id, s.current_phase, s.started_at
HAVING COUNT(ph.history_id) <= 1  -- 초기 Phase만 있거나 전환 없음
  AND NOW() - s.started_at > INTERVAL '30 minutes'
ORDER BY session_duration DESC;


-- ####################################################################
-- [작업영역 8] 데이터 관리 (삭제/정리)
-- ####################################################################

-- --------------------------------------------------------------------
-- 8-1. 특정 세션의 Phase 이력 전체 삭제
-- 용도: 테스트 데이터 정리
-- ⚠️ 주의: 히스토리 데이터 영구 삭제
-- --------------------------------------------------------------------

DELETE FROM phase_history
WHERE session_id = $1;


-- --------------------------------------------------------------------
-- 8-2. 오래된 Phase 이력 정리 (보관 기간 초과)
-- 용도: 디스크 공간 확보
-- --------------------------------------------------------------------

-- 90일 이상 지난 종료 세션의 Phase 이력 삭제
DELETE FROM phase_history
WHERE session_id IN (
    SELECT session_id
    FROM session
    WHERE status = 'ended'
      AND ended_at < NOW() - INTERVAL '90 days'
);


-- --------------------------------------------------------------------
-- 8-3. 특정 Phase 전환 기록만 삭제
-- 용도: 잘못 기록된 특정 이력 삭제
-- --------------------------------------------------------------------

DELETE FROM phase_history
WHERE history_id = $1;


-- ####################################################################
-- [작업영역 9] 리포트 생성 (분석/통계)
-- ####################################################################

-- --------------------------------------------------------------------
-- 9-1. Phase 전환 요약 리포트
-- 용도: 세션 종료 후 플레이 리뷰
-- --------------------------------------------------------------------

WITH phase_summary AS (
    SELECT
        new_phase,
        COUNT(*) AS transition_count,
        MIN(transitioned_at) AS first_transition,
        MAX(transitioned_at) AS last_transition,
        SUM(
            LEAD(transitioned_at, 1, NOW()) OVER (ORDER BY transitioned_at)
            - transitioned_at
        ) AS total_duration
    FROM phase_history
    WHERE session_id = $1
    GROUP BY new_phase
)
SELECT
    new_phase AS phase,
    transition_count,
    total_duration,
    total_duration / NULLIF(transition_count, 0) AS avg_duration_per_visit,
    first_transition,
    last_transition
FROM phase_summary
ORDER BY total_duration DESC;


-- --------------------------------------------------------------------
-- 9-2. 시간대별 Phase 분포 히트맵 데이터
-- 용도: 시각화 대시보드
-- --------------------------------------------------------------------

SELECT
    DATE(transitioned_at) AS date,
    EXTRACT(HOUR FROM transitioned_at) AS hour,
    new_phase,
    COUNT(*) AS transition_count
FROM phase_history
WHERE session_id = $1
GROUP BY date, hour, new_phase
ORDER BY date, hour, new_phase;


-- --------------------------------------------------------------------
-- 9-3. Phase 전환 타임라인 (JSON 형식)
-- 용도: 프론트엔드 타임라인 UI
-- --------------------------------------------------------------------

SELECT jsonb_agg(
    jsonb_build_object(
        'timestamp', transitioned_at,
        'from', previous_phase,
        'to', new_phase,
        'turn', turn_at_transition,
        'reason', transition_reason
    ) ORDER BY transitioned_at
) AS phase_timeline
FROM phase_history
WHERE session_id = $1;


-- ####################################################################
-- [작업영역 10] 테스트 및 유틸리티
-- ####################################################################

-- --------------------------------------------------------------------
-- 10-1. Phase 이력 전체 덤프 (디버깅용)
-- 용도: 문제 발생 시 전체 이력 확인
-- --------------------------------------------------------------------

SELECT
    history_id,
    session_id,
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
FROM phase_history
WHERE session_id = $1
ORDER BY transitioned_at ASC;


-- --------------------------------------------------------------------
-- 10-2. Phase 전환 테스트 데이터 생성
-- 용도: 개발/테스트 환경
-- --------------------------------------------------------------------

-- 수동으로 Phase 이력 삽입 (트리거 우회)
INSERT INTO phase_history (
    session_id,
    previous_phase,
    new_phase,
    turn_at_transition,
    transition_reason,
    transitioned_at
)
VALUES
    ($1, NULL, 'dialogue', 0, 'session_start', NOW() - INTERVAL '1 hour'),
    ($1, 'dialogue', 'exploration', 1, 'story_progression', NOW() - INTERVAL '50 minutes'),
    ($1, 'exploration', 'combat', 5, 'enemy_encounter', NOW() - INTERVAL '30 minutes'),
    ($1, 'combat', 'exploration', 12, 'combat_victory', NOW() - INTERVAL '10 minutes');


-- --------------------------------------------------------------------
-- 10-3. Phase 이력 존재 여부 확인
-- 용도: 테스트 검증
-- --------------------------------------------------------------------

SELECT EXISTS(
    SELECT 1
    FROM phase_history
    WHERE session_id = $1
) AS has_phase_history;


-- --------------------------------------------------------------------
-- 10-4. 세션별 Phase 이력 카운트
-- 용도: 데이터 무결성 확인
-- --------------------------------------------------------------------

SELECT
    session_id,
    COUNT(*) AS phase_transition_count,
    MIN(transitioned_at) AS first_transition,
    MAX(transitioned_at) AS last_transition
FROM phase_history
GROUP BY session_id
ORDER BY phase_transition_count DESC;


-- ====================================================================
-- 파일 끝
-- ====================================================================
