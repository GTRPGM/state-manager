-- API 키 삭제 (소프트 삭제: is_active를 false로)
-- $1: api_key_id

UPDATE api_keys
SET is_active = false
WHERE api_key_id = $1
RETURNING api_key_id, key_name;
