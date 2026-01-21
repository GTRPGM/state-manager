-- ability.sql
-- Rule Engine 기반 Ability Node 정의
-- state_DB는 ability의 식별자와 메타 정보만 관리

CREATE TABLE IF NOT EXISTS ability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Rule Engine의 ability 고유 ID
    rule_ability_id UUID NOT NULL UNIQUE,

    entity_type VARCHAR(50) NOT NULL DEFAULT 'ability',

    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',

    -- 분류용 (확장 가능)
    ability_type VARCHAR(50) DEFAULT 'active',

    -- Rule 메타 정보 (버전, 조건 요약 등)
    meta JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
