-- ability.sql
-- Rule Engine 기반 Ability Node 정의
-- state_db는 ability의 식별자와 meta 정보만 관리
-- 모든 ability는 session_id에 종속

CREATE TABLE IF NOT EXISTS ability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Rule Engine의 ability 고유 ID
    rule_ability_id UUID NOT NULL UNIQUE,

    -- 엔티티 유형
    entity_type VARCHAR(50) NOT NULL DEFAULT 'ability',

    -- 세션 참조 (모든 Node는 session_id에 종속)
    session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,

    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',

    -- 분류용 (확장 가능)
    ability_type VARCHAR(50) DEFAULT 'active',

    -- Rule 메타 정보 (버전, 조건 요약 등)
    meta JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- updated_at 자동 갱신 트리거 | 불필요할것으로 예상함
CREATE OR REPLACE FUNCTION update_ability_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ability_updated_at
BEFORE UPDATE ON ability
FOR EACH ROW
EXECUTE FUNCTION update_ability_updated_at();
