-- player_dml.sql
-- Player 엔티티 DML (Data Manipulation Language)
-- 세션 시작 시 사용자 입력으로 생성
-- state_db에서 관리

-- ========================================
-- 1. CREATE - 플레이어 생성
-- ========================================
-- 세션 시작 직후, 사용자 입력 받아 생성
-- Parameters:
--   :session_id  - 방금 생성된 세션 UUID
--   :name        - 플레이어 이름 (사용자 입력)
--   :description - 플레이어 설명 (사용자 입력)
--   :STR, :DEX, :INT, :LUX, :SAN - 능력치 (사용자 입력, NULL 가능)

INSERT INTO player (
    session_id,
    name,
    description,
    state
) VALUES (
    :session_id,
    :name,
    :description,
    jsonb_build_object(
        'numeric', jsonb_build_object(
            'HP', 100,
            'MP', 50,
            'STR', :STR,
            'DEX', :DEX,
            'INT', :INT,
            'LUX', :LUX,
            'SAN', :SAN
        ),
        'boolean', '{}'::jsonb
    )
)
RETURNING
    id AS player_id,
    name,
    session_id,
    created_at;


-- ========================================
-- 2. READ - 플레이어 조회
-- ========================================

-- 2-1. 특정 플레이어 조회 (ID로)
SELECT
    id,
    entity_type,
    name,
    description,
    session_id,
    created_at,
    updated_at,
    tags,
    state,
    relations
FROM player
WHERE id = :player_id
  AND session_id = :session_id;


-- 2-2. 세션의 모든 플레이어 조회
SELECT
    id,
    name,
    state->'numeric'->>'HP' AS hp,
    state->'numeric'->>'MP' AS mp,
    created_at
FROM player
WHERE session_id = :session_id
ORDER BY created_at ASC;


-- 2-3. 플레이어 능력치 조회
SELECT
    id,
    name,
    state->'numeric' AS stats
FROM player
WHERE id = :player_id
  AND session_id = :session_id;


-- ========================================
-- 3. UPDATE - 플레이어 정보 업데이트
-- ========================================

-- 3-1. HP/MP 업데이트 (전투, 회복 등)
UPDATE player
SET
    state = jsonb_set(
        jsonb_set(
            state,
            '{numeric, HP}',
            to_jsonb(:new_hp)
        ),
        '{numeric, MP}',
        to_jsonb(:new_mp)
    ),
    updated_at = NOW()
WHERE id = :player_id
  AND session_id = :session_id
RETURNING
    id,
    state->'numeric'->>'HP' AS hp,
    state->'numeric'->>'MP' AS mp;


-- 3-2. 특정 능력치 업데이트 (레벨업 등)
UPDATE player
SET
    state = jsonb_set(
        state,
        :stat_path,  -- 예: '{numeric, STR}'
        to_jsonb(:new_value)
    ),
    updated_at = NOW()
WHERE id = :player_id
  AND session_id = :session_id
RETURNING
    id,
    state->'numeric' AS stats;


-- 3-3. 상태 효과 업데이트 (boolean)
UPDATE player
SET
    state = jsonb_set(
        state,
        '{boolean, ' || :status_name || '}',  -- 예: poisoned
        to_jsonb(:status_value::boolean)
    ),
    updated_at = NOW()
WHERE id = :player_id
  AND session_id = :session_id
RETURNING
    id,
    state->'boolean' AS status_effects;


-- 3-4. RELATION 추가 (관계 생성 시)
UPDATE player
SET
    relations = relations || jsonb_build_array(:relation_id),
    updated_at = NOW()
WHERE id = :player_id
  AND session_id = :session_id
RETURNING
    id,
    relations;


-- 3-5. RELATION 제거 (관계 삭제 시)
UPDATE player
SET
    relations = (
        SELECT jsonb_agg(elem)
        FROM jsonb_array_elements(relations) AS elem
        WHERE elem::text != to_jsonb(:relation_id)::text
    ),
    updated_at = NOW()
WHERE id = :player_id
  AND session_id = :session_id
RETURNING
    id,
    relations;


-- 3-6. 설명/태그 업데이트
UPDATE player
SET
    description = :new_description,
    tags = :new_tags,
    updated_at = NOW()
WHERE id = :player_id
  AND session_id = :session_id
RETURNING
    id,
    description,
    tags;


-- ========================================
-- 4. DELETE - 플레이어 삭제
-- ========================================

-- 4-1. 특정 플레이어 삭제 (세션 중단 시)
-- 주의: CASCADE로 인해 관련 RELATION 엣지도 함께 삭제됨
DELETE FROM player
WHERE id = :player_id
  AND session_id = :session_id
RETURNING
    id,
    name,
    session_id;


-- 4-2. 세션의 모든 플레이어 삭제 (세션 종료 시)
-- 주의: session 삭제 시 자동 CASCADE되므로 직접 호출 불필요
DELETE FROM player
WHERE session_id = :session_id
RETURNING
    count(*) AS deleted_count;


-- ========================================
-- 5. 복합 쿼리 - 실전 사용 예시
-- ========================================

-- 5-1. 전투 데미지 처리 (HP 감소)
UPDATE player
SET
    state = jsonb_set(
        state,
        '{numeric, HP}',
        to_jsonb(
            GREATEST(
                0,
                (state->'numeric'->>'HP')::int - :damage
            )
        )
    ),
    updated_at = NOW()
WHERE id = :player_id
  AND session_id = :session_id
RETURNING
    id,
    name,
    (state->'numeric'->>'HP')::int AS current_hp,
    CASE
        WHEN (state->'numeric'->>'HP')::int <= 0 THEN true
        ELSE false
    END AS is_dead;


-- 5-2. 회복 아이템 사용 (HP 회복, 최대치 제한)
UPDATE player
SET
    state = jsonb_set(
        state,
        '{numeric, HP}',
        to_jsonb(
            LEAST(
                100,  -- 최대 HP
                (state->'numeric'->>'HP')::int + :heal_amount
            )
        )
    ),
    updated_at = NOW()
WHERE id = :player_id
  AND session_id = :session_id
RETURNING
    id,
    (state->'numeric'->>'HP')::int AS current_hp;


-- -- 5-3. 레벨업 (여러 능력치 동시 증가)
-- UPDATE player
-- SET
--     state = jsonb_set(
--         jsonb_set(
--             jsonb_set(
--                 state,
--                 '{numeric, STR}',
--                 to_jsonb((state->'numeric'->>'STR')::int + :str_gain)
--             ),
--             '{numeric, DEX}',
--             to_jsonb((state->'numeric'->>'DEX')::int + :dex_gain)
--         ),
--         '{numeric, INT}',
--         to_jsonb((state->'numeric'->>'INT')::int + :int_gain)
--     ),
--     updated_at = NOW()
-- WHERE id = :player_id
--   AND session_id = :session_id
-- RETURNING
--     id,
--     state->'numeric' AS new_stats;
