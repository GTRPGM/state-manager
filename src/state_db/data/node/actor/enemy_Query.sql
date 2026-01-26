-- enemy_dml.sql
-- Enemy 엔티티 DML (Data Manipulation Language)
-- 세션 시작 시 시나리오에서 전달받아 생성
-- 전투 중심 엔티티, 드롭 아이템 관리

-- ========================================
-- 1. CREATE - Enemy 생성
-- ========================================
-- 세션 시작 시 시나리오로부터 전달받아 생성
-- Parameters:
--   :enemy_id          - Enemy UUID (시나리오 전달)
--   :session_id        - 현재 세션 UUID
--   :scenario_id       - 시나리오 UUID
--   :scenario_enemy_id - 시나리오 내 Enemy ID
--   :name              - Enemy 이름
--   :description       - Enemy 설명
--   :HP, :STR...       - 능력치 (시나리오 전달)

INSERT INTO enemy (
    enemy_id,
    session_id,
    scenario_id,
    scenario_enemy_id,
    name,
    description,
    tags,
    state
) VALUES (
    :enemy_id,
    :session_id,
    :scenario_id,
    :scenario_enemy_id,
    :name,
    :description,
    :tags,  -- 예: ARRAY['enemy', 'melee', 'goblin']
    jsonb_build_object(
        'numeric', jsonb_build_object(
            'HP', :HP,
            'MP', coalesce(:MP, 0),
            'STR', :STR,
            'DEX', :DEX,
            'INT', :INT,
            'LUX', null,
            'SAN', null
        ),
        'boolean', '{}'::jsonb
    )
)
RETURNING
    enemy_id,
    name,
    scenario_id,
    created_at;


-- ========================================
-- 2. READ - Enemy 조회
-- ========================================

-- -- 2-1. 특정 Enemy 조회
-- SELECT
--     enemy_id,
--     entity_type,
--     name,
--     description,
--     session_id,
--     scenario_id,
--     scenario_enemy_id,
--     created_at,
--     updated_at,
--     tags,
--     state,
--     relations,
--     dropped_items
-- FROM enemy
-- WHERE enemy_id = :enemy_id
--   AND session_id = :session_id;


-- -- 2-2. 세션의 모든 Enemy 조회
-- SELECT
--     enemy_id,
--     name,
--     tags,
--     state->'numeric'->>'HP' AS hp,
--     created_at
-- FROM enemy
-- WHERE session_id = :session_id
-- ORDER BY created_at ASC;


-- -- 2-3. 시나리오별 Enemy 조회
-- SELECT
--     enemy_id,
--     scenario_enemy_id,
--     name,
--     tags,
--     (state->'numeric'->>'HP')::int AS hp
-- FROM enemy
-- WHERE session_id = :session_id
--   AND scenario_id = :scenario_id;


-- -- 2-4. 태그로 Enemy 필터링 (예: melee 타입만)
-- SELECT
--     enemy_id,
--     name,
--     description,
--     tags
-- FROM enemy
-- WHERE session_id = :session_id
--   AND :tag = ANY(tags);


-- 2-5. 살아있는 Enemy만 조회 (HP > 0)
SELECT
    enemy_id,
    name,
    (state->'numeric'->>'HP')::int AS hp,
    tags
FROM enemy
WHERE session_id = :session_id
  AND (state->'numeric'->>'HP')::int > 0
ORDER BY name;


-- -- 2-6. 드롭한 아이템이 있는 Enemy 조회
-- SELECT
--     enemy_id,
--     name,
--     dropped_items,
--     array_length(dropped_items, 1) AS drop_count
-- FROM enemy
-- WHERE session_id = :session_id
--   AND array_length(dropped_items, 1) > 0;


-- ========================================
-- 3. UPDATE - Enemy 정보 업데이트
-- ========================================

-- 3-1. HP 업데이트 (전투 데미지)
UPDATE enemy
SET
    state = jsonb_set(
        state,
        '{numeric, HP}',
        to_jsonb(:new_hp)
    ),
    updated_at = NOW()
WHERE enemy_id = :enemy_id
  AND session_id = :session_id
RETURNING
    enemy_id,
    name,
    state->'numeric'->>'HP' AS hp;


-- -- 3-2. 상태 효과 추가 (boolean)
-- UPDATE enemy
-- SET
--     state = jsonb_set(
--         state,
--         '{boolean, ' || :status_name || '}',
--         to_jsonb(:status_value::boolean)
--     ),
--     updated_at = NOW()
-- WHERE enemy_id = :enemy_id
--   AND session_id = :session_id
-- RETURNING
--     enemy_id,
--     state->'boolean' AS status_effects;


-- 3-3. RELATION 추가 (관계 생성 시)
UPDATE enemy
SET
    relations = relations || jsonb_build_array(:relation_id),
    updated_at = NOW()
WHERE enemy_id = :enemy_id
  AND session_id = :session_id
RETURNING
    enemy_id,
    relations;


-- 3-4. RELATION 제거
UPDATE enemy
SET
    relations = (
        SELECT jsonb_agg(elem)
        FROM jsonb_array_elements(relations) AS elem
        WHERE elem::text != to_jsonb(:relation_id)::text
    ),
    updated_at = NOW()
WHERE enemy_id = :enemy_id
  AND session_id = :session_id
RETURNING
    enemy_id,
    relations;


-- -- 3-5. dropped_items 배열에 아이템 추가
-- UPDATE enemy
-- SET
--     dropped_items = array_append(dropped_items, :item_id),
--     updated_at = NOW()
-- WHERE enemy_id = :enemy_id
--   AND session_id = :session_id
-- RETURNING
--     enemy_id,
--     dropped_items;


-- -- 3-6. dropped_items 배열 초기화 (재사용 시)
-- UPDATE enemy
-- SET
--     dropped_items = ARRAY[]::UUID[],
--     updated_at = NOW()
-- WHERE enemy_id = :enemy_id
--   AND session_id = :session_id
-- RETURNING
--     enemy_id;


-- ========================================
-- 4. DELETE - Enemy 삭제
-- ========================================

-- 4-1. 특정 Enemy 삭제 (사망, 도망 등)
DELETE FROM enemy
WHERE enemy_id = :enemy_id
  AND session_id = :session_id
RETURNING
    enemy_id,
    name,
    scenario_id,
    dropped_items;


-- 4-2. HP 0 이하인 Enemy 일괄 삭제
DELETE FROM enemy
WHERE session_id = :session_id
  AND (state->'numeric'->>'HP')::int <= 0
RETURNING
    enemy_id,
    name,
    dropped_items;


-- 4-3. 시나리오의 모든 Enemy 삭제
DELETE FROM enemy
WHERE session_id = :session_id
  AND scenario_id = :scenario_id
RETURNING
    count(*) AS deleted_count;


-- 4-4. 세션의 모든 Enemy 삭제 (세션 종료 시)
-- 주의: CASCADE로 자동 처리
DELETE FROM enemy
WHERE session_id = :session_id
RETURNING
    count(*) AS deleted_count;


-- ========================================
-- 5. 복합 쿼리 - 실전 사용 예시
-- ========================================

-- 5-1. 전투 데미지 처리 (HP 감소, 사망 판정)
UPDATE enemy
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
WHERE enemy_id = :enemy_id
  AND session_id = :session_id
RETURNING
    enemy_id,
    name,
    (state->'numeric'->>'HP')::int AS current_hp,
    CASE
        WHEN (state->'numeric'->>'HP')::int <= 0 THEN true
        ELSE false
    END AS is_defeated,
    dropped_items;


-- -- 5-2. Enemy 사망 시 드롭 처리 (DROP_ITEM 엣지 결과 받아서)
-- -- DROP_ITEM 엣지에서 확률 판정 후 dropped_items 배열 업데이트
-- UPDATE enemy
-- SET
--     dropped_items = array_append(dropped_items, :item_id),
--     state = jsonb_set(
--         state,
--         '{numeric, HP}',
--         to_jsonb(0)
--     ),
--     updated_at = NOW()
-- WHERE enemy_id = :enemy_id
--   AND session_id = :session_id
--   AND (state->'numeric'->>'HP')::int <= 0
-- RETURNING
--     enemy_id,
--     name,
--     dropped_items;


-- -- 5-3. 전투 난이도 계산 (총 Enemy HP)
-- SELECT
--     SUM((state->'numeric'->>'HP')::int) AS total_enemy_hp,
--     COUNT(*) AS enemy_count,
--     AVG((state->'numeric'->>'STR')::int) AS avg_strength
-- FROM enemy
-- WHERE session_id = :session_id
--   AND (state->'numeric'->>'HP')::int > 0;


-- -- 5-4. 가장 강한 Enemy 조회 (STR 기준)
-- SELECT
--     enemy_id,
--     name,
--     (state->'numeric'->>'HP')::int AS hp,
--     (state->'numeric'->>'STR')::int AS strength
-- FROM enemy
-- WHERE session_id = :session_id
--   AND (state->'numeric'->>'HP')::int > 0
-- ORDER BY (state->'numeric'->>'STR')::int DESC
-- LIMIT 1;


-- -- 5-5. Enemy 타입별 집계 (태그 기준)
-- SELECT
--     unnest(tags) AS enemy_type,
--     COUNT(*) AS count,
--     SUM((state->'numeric'->>'HP')::int) AS total_hp
-- FROM enemy
-- WHERE session_id = :session_id
--   AND (state->'numeric'->>'HP')::int > 0
-- GROUP BY enemy_type
-- ORDER BY count DESC;


-- 5-6. 플레이어와 적대 관계인 Enemy 조회
-- (RELATION 엣지와 조인)
WITH player_hostile_relations AS (
    SELECT jsonb_array_elements(relations) AS relation_id
    FROM player
    WHERE id = :player_id
      AND session_id = :session_id
)
SELECT
    e.enemy_id,
    e.name,
    e.state->'numeric'->>'HP' AS hp,
    e.relations
FROM enemy e
WHERE e.session_id = :session_id
  AND e.relations ?| ARRAY(SELECT relation_id::text FROM player_hostile_relations);


-- 5-7. 전투 후 생존 Enemy 목록 (HP > 0, 드롭 없음)
SELECT
    enemy_id,
    name,
    (state->'numeric'->>'HP')::int AS hp,
    array_length(dropped_items, 1) AS items_dropped
FROM enemy
WHERE session_id = :session_id
  AND (state->'numeric'->>'HP')::int > 0
ORDER BY (state->'numeric'->>'HP')::int DESC;
