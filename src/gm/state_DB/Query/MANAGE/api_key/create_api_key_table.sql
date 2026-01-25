-- API 키 테이블 생성
-- API 인증을 위한 키 정보 저장

CREATE TABLE IF NOT EXISTS api_keys (
    api_key_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash TEXT NOT NULL UNIQUE,  -- SHA-256 해시된 API 키
    key_name TEXT NOT NULL,         -- API 키 이름 (식별용)
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- 인덱스 생성 (검색 최적화)
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);

-- 코멘트 추가
COMMENT ON TABLE api_keys IS 'API 인증키 관리 테이블';
COMMENT ON COLUMN api_keys.key_hash IS 'SHA-256 해시된 API 키 (원본은 저장하지 않음)';
COMMENT ON COLUMN api_keys.key_name IS 'API 키 식별용 이름';
COMMENT ON COLUMN api_keys.last_used_at IS '마지막으로 API 키가 사용된 시각';
