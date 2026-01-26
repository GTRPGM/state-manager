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
