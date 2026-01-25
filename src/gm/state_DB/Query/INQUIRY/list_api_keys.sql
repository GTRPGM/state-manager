-- 모든 API 키 목록 조회 (해시는 제외)

SELECT
    api_key_id,
    key_name,
    created_at,
    last_used_at,
    is_active
FROM api_keys
ORDER BY created_at DESC;
