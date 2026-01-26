-- --------------------------------------------------------------------
-- spawn_npc.sql
-- NPC 동적 생성
-- 용도: 이벤트로 NPC 등장 또는 GM 명령
-- API: POST /state/session/{session_id}/npc/spawn
-- --------------------------------------------------------------------

-- NPC 인스턴스 생성
INSERT INTO npc (
    session_id,
    npc_id,
    name,
    description,
    state,
    tags
)
VALUES (
    $1,  -- session_id
    $2,  -- npc_id (NPC 종류 ID)
    $3,  -- name
    COALESCE($4, ''),  -- description
    jsonb_build_object(
        'numeric', jsonb_build_object(
            'HP', COALESCE($5, 100),  -- hp
            'max_hp', COALESCE($5, 100)  -- max_hp
        ),
        'boolean', '{}'::jsonb
    ),
    COALESCE($6, ARRAY['npc']::TEXT[])  -- tags
)
RETURNING
    npc_instance_id,
    npc_id,
    name,
    description,
    state,
    tags,
    created_at;

-- 파라미터:
-- $1: session_id (UUID)
-- $2: npc_id (INTEGER) - NPC 종류 ID
-- $3: name (VARCHAR)
-- $4: description (TEXT) - 선택적
-- $5: hp (INTEGER) - 선택적, 기본값 100
-- $6: tags (TEXT[]) - 선택적

-- 결과 예:
-- npc_instance_id | npc_id | name         | description           | state
-- ----------------|--------|--------------|----------------------|------------------
-- uuid-new        | 5      | Merchant Tom | A friendly merchant  | {"numeric": {...}}

-- 사용 예:
-- 특정 위치에 도착했을 때 NPC 등장
-- 퀘스트 진행으로 NPC 생성
-- GM이 동적으로 NPC 추가
