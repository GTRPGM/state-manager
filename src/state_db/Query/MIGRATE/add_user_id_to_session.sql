-- --------------------------------------------------------------------
-- add_user_id_to_session.sql
-- 마이그레이션: session 테이블에 user_id 컬럼 추가
-- 실행 시점: 기존 DB에 적용 시
-- --------------------------------------------------------------------

ALTER TABLE session ADD COLUMN IF NOT EXISTS user_id INTEGER DEFAULT NULL;
CREATE INDEX IF NOT EXISTS idx_session_user_id ON session(user_id);

COMMENT ON COLUMN session.user_id IS '외부 시스템의 사용자 식별자 (Optional, FK 없음, INTEGER)';
