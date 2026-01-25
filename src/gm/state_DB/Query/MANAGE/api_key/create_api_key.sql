-- API 키 생성
-- $1: key_hash (SHA-256 해시된 키)
-- $2: key_name (키 이름)

INSERT INTO api_keys (key_hash, key_name)
VALUES ($1, $2)
RETURNING api_key_id, key_name, created_at, is_active;
