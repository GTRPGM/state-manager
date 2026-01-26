-- npc_dml.sql
-- NPC 엔티티 DML (Data Manipulation Language)
-- 세션 시작 시 시나리오에서 전달받아 생성
-- 시나리오에 종속

-- ========================================
-- 1. CREATE - NPC 생성
-- ========================================
-- 세션 시작 시 시나리오로부터 전달받아 생성
-- Parameters:
--   :npc_id          - NPC UUID (시나리오 전달)
--   :session_id      - 현재 세션 UUID
--   :scenario_id     - 시나리오 UUID
--   :scenario_npc_id - 시나리오 내 NPC ID
--   :name            - NPC 이름
--   :description     - NPC 설명
--   :HP, :MP, :STR... - 능력치 (시나리오 전달)

INSERT INTO npc (
    npc_id,
    session_id,
    scenario_id,
    scenario_npc_id,
    name,
    description,
    tags,
    state
) VALUES (
    :npc_id,
    :session_id,
    :scenario_id,
    :scenario_npc_id,
    :name,
    :description,
    :tags,  -- 예: ARRAY['npc', 'merchant', 'quest_giver']
    jsonb_build_object(
        'numeric', jsonb_build_object(
            'HP', :HP,
            'MP', :MP,
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
    npc_id,
    name,
    scenario_id,
    created_at;


-- ========================================
-- 2. READ - NPC 조회
-- ========================================

-- -- 2-1. 특정 NPC 조회
-- SELECT
--     npc_id,
--     entity_type,
--     name,
--     description,
--     session_id,
--     scenario_id,
--     scenario_npc_id,
--     created_at,
--     updated_at,
--     tags,
--     state,
--     relations
-- FROM npc
-- WHERE npc_id = :npc_id
--   AND session_id = :session_id;


-- -- 2-2. 세션의 모든 NPC 조회
-- SELECT
--     npc_id,
--     name,
--     tags,
--     state->'numeric'->>'HP' AS hp,
--     created_at
-- FROM npc
-- WHERE session_id = :session_id
-- ORDER BY created_at ASC;


-- -- 2-3. 시나리오별 NPC 조회
-- SELECT
--     npc_id,
--     scenario_npc_id,
--     name,
--     tags
-- FROM npc
-- WHERE session_id = :session_id
--   AND scenario_id = :scenario_id;


-- -- 2-4. 태그로 NPC 필터링 (예: 상인만)
-- SELECT
--     npc_id,
--     name,
--     description,
--     tags
-- FROM npc
-- WHERE session_id = :session_id
--   AND :tag = ANY(tags);  -- 예: 'merchant'


-- -- 2-5. 특정 플레이어와 관계 있는 NPC 조회
-- SELECT
--     n.npc_id,
--     n.name,
--     n.tags,
--     n.relations
-- FROM npc n
-- WHERE n.session_id = :session_id
--   AND n.relations @> to_jsonb(ARRAY[:relation_id]);  -- relation_id 포함 여부


-- ========================================
-- 3. UPDATE - NPC 정보 업데이트
-- ========================================

-- 3-1. HP/MP 업데이트 (전투, 상호작용)
UPDATE npc
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
WHERE npc_id = :npc_id
  AND session_id = :session_id
RETURNING
    npc_id,
    name,
    state->'numeric'->>'HP' AS hp,
    state->'numeric'->>'MP' AS mp;


-- 3-2. 상태 효과 추가 (boolean)
UPDATE npc
SET
    state = jsonb_set(
        state,
        '{boolean, ' || :status_name || '}',
        to_jsonb(:status_value::boolean)
    ),
    updated_at = NOW()
WHERE npc_id = :npc_id
  AND session_id = :session_id
RETURNING
    npc_id,
    state->'boolean' AS status_effects;


-- 3-3. RELATION 추가 (관계 생성 시)
UPDATE npc
SET
    relations = relations || jsonb_build_array(:relation_id),
    updated_at = NOW()
WHERE npc_id = :npc_id
  AND session_id = :session_id
RETURNING
    npc_id,
    relations;


-- 3-4. RELATION 제거 (관계 삭제/비활성화 시)
UPDATE npc
SET
    relations = (
        SELECT jsonb_agg(elem)
        FROM jsonb_array_elements(relations) AS elem
        WHERE elem::text != to_jsonb(:relation_id)::text
    ),
    updated_at = NOW()
WHERE npc_id = :npc_id
  AND session_id = :session_id
RETURNING
    npc_id,
    relations;


-- 3-5. 태그 추가/수정 (이벤트에 따라)
UPDATE npc
SET
    tags = array_append(tags, :new_tag),
    updated_at = NOW()
WHERE npc_id = :npc_id
  AND session_id = :session_id
  AND NOT (:new_tag = ANY(tags))  -- 중복 방지
RETURNING
    npc_id,
    tags;


-- 3-6. 설명 업데이트 (스토리 진행에 따라)
UPDATE npc
SET
    description = :new_description,
    updated_at = NOW()
WHERE npc_id = :npc_id
  AND session_id = :session_id
RETURNING
    npc_id,
    description;


-- ========================================
-- 4. DELETE - NPC 삭제
-- ========================================

-- 4-1. 특정 NPC 삭제 (퇴장, 사망 등)
-- 주의: 실제로는 시나리오 이벤트로 관리하므로 직접 DELETE는 드묾
DELETE FROM npc
WHERE npc_id = :npc_id
  AND session_id = :session_id
RETURNING
    npc_id,
    name,
    scenario_id;


-- 4-2. 시나리오의 모든 NPC 삭제
DELETE FROM npc
WHERE session_id = :session_id
  AND scenario_id = :scenario_id
RETURNING
    count(*) AS deleted_count;


-- 4-3. 세션의 모든 NPC 삭제 (세션 종료 시)
-- 주의: CASCADE로 자동 처리되므로 직접 호출 불필요
DELETE FROM npc
WHERE session_id = :session_id
RETURNING
    count(*) AS deleted_count;


-- ========================================
-- 5. 복합 쿼리 - 실전 사용 예시
-- ========================================

-- 5-1. NPC 전투 데미지 처리
UPDATE npc
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
WHERE npc_id = :npc_id
  AND session_id = :session_id
RETURNING
    npc_id,
    name,
    (state->'numeric'->>'HP')::int AS current_hp,
    CASE
        WHEN (state->'numeric'->>'HP')::int <= 0 THEN true
        ELSE false
    END AS is_defeated;


-- -- 5-2. 상인 NPC 거래 가능 여부 확인
-- SELECT
--     npc_id,
--     name,
--     description,
--     CASE
--         WHEN 'merchant' = ANY(tags) THEN true
--         ELSE false
--     END AS can_trade,
--     state->'numeric'->>'HP' AS hp
-- FROM npc
-- WHERE npc_id = :npc_id
--   AND session_id = :session_id;


-- -- 5-3. 플레이어와 우호 관계인 NPC 목록
-- -- (RELATION 엣지와 조인 필요)
-- WITH player_relations AS (
--     SELECT relations
--     FROM player
--     WHERE id = :player_id
--       AND session_id = :session_id
-- )
-- SELECT
--     n.npc_id,
--     n.name,
--     n.tags,
--     n.relations
-- FROM npc n, player_relations pr
-- WHERE n.session_id = :session_id
--   AND n.relations && pr.relations  -- JSONB 배열 교집합
-- ORDER BY n.name;


-- 5-4. 살아있는 NPC만 조회 (HP > 0)
SELECT
    npc_id,
    name,
    (state->'numeric'->>'HP')::int AS hp
FROM npc
WHERE session_id = :session_id
  AND (state->'numeric'->>'HP')::int > 0
ORDER BY name;


-- -- 5-5. NPC 능력치 랭킹 (STR 높은 순)
-- SELECT
--     npc_id,
--     name,
--     (state->'numeric'->>'STR')::int AS strength
-- FROM npc
-- WHERE session_id = :session_id
--   AND state->'numeric'->>'STR' IS NOT NULL
-- ORDER BY (state->'numeric'->>'STR')::int DESC
-- LIMIT 10;
