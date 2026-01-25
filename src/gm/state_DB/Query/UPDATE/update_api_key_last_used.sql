-- API 키 마지막 사용 시각 업데이트
-- $1: key_hash

UPDATE api_keys
SET last_used_at = NOW()
WHERE key_hash = $1 AND is_active = true;
