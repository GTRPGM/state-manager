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
