-- --------------------------------------------------------------------
-- 1-5. Act 변경 가능 여부 확인
-- 용도: Act 전환 조건 검증
-- 예: "현재 Sequence를 모두 완료했는가"
-- --------------------------------------------------------------------

SELECT
    current_act,
    current_sequence,
    -- 예시: Sequence 5까지 완료해야 다음 Act로 진행 가능
    CASE
        WHEN current_sequence >= 5 THEN true
        ELSE false
    END AS can_advance_act
FROM session
WHERE session_id = $1;
