-- API 키 검증 및 조회
-- $1: key_hash (SHA-256 해시된 키)

SELECT
    api_key_id,
    key_name,
    created_at,
    last_used_at,
    is_active
FROM api_keys
WHERE key_hash = $1 AND is_active = true;
