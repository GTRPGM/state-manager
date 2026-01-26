-- --------------------------------------------------------------------
-- spawn_enemy.sql
-- 적 동적 생성
-- 용도: 전투 시작 시 또는 이벤트로 적 생성
-- API: POST /state/session/{session_id}/enemy/spawn
-- --------------------------------------------------------------------

-- 적 인스턴스 생성
INSERT INTO enemy (
    session_id,
    enemy_id,
    name,
    description,
    state,
    tags
)
VALUES (
    $1,  -- session_id
    $2,  -- enemy_id (적 종류 ID)
    $3,  -- name
    COALESCE($4, ''),  -- description
    jsonb_build_object(
        'numeric', jsonb_build_object(
            'HP', COALESCE($5, 30),      -- hp
            'max_hp', COALESCE($5, 30),  -- max_hp
            'ATK', COALESCE($6, 10),     -- attack
            'DEF', COALESCE($7, 5)       -- defense
        ),
        'boolean', '{}'::jsonb
    ),
    COALESCE($8, ARRAY['enemy']::TEXT[])  -- tags
)
RETURNING
    enemy_instance_id,
    enemy_id,
    name,
    description,
    state,
    is_defeated,
    created_at;

-- 파라미터:
-- $1: session_id (UUID)
-- $2: enemy_id (INTEGER) - 적 종류 ID
-- $3: name (VARCHAR)
-- $4: description (TEXT) - 선택적
-- $5: hp (INTEGER) - 선택적, 기본값 30
-- $6: attack (INTEGER) - 선택적, 기본값 10
-- $7: defense (INTEGER) - 선택적, 기본값 5
-- $8: tags (TEXT[]) - 선택적

-- 결과 예:
-- enemy_instance_id | enemy_id | name           | state                    | is_defeated
-- ------------------|----------|----------------|--------------------------|-------------
-- uuid-new          | 1        | Goblin Warrior | {"numeric": {"HP": 30}}  | false

-- 사용 예:
-- Phase가 combat으로 전환될 때
-- 특정 이벤트 트리거 시
