-- ====================================================================
-- L_player_npc_relations.sql
-- 관계 초기화 및 상호작용 업데이트 로직 (Logic)
-- ====================================================================

-- 1. 상호작용 시 자동으로 카운터 증가 및 시간 기록 트리거
CREATE OR REPLACE FUNCTION update_npc_interaction()
RETURNS TRIGGER AS $$
BEGIN
    -- 호감도 수치에 변화가 생겼을 때만 상호작용으로 간주
    IF OLD.affinity_score IS DISTINCT FROM NEW.affinity_score THEN
        NEW.interaction_count = OLD.interaction_count + 1;
        NEW.last_interaction_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_npc_interaction ON player_npc_relations;
CREATE TRIGGER trg_npc_interaction
BEFORE UPDATE ON player_npc_relations
FOR EACH ROW
EXECUTE FUNCTION update_npc_interaction();

-- 2. 세션 생성 시 모든 NPC와의 관계 레코드 생성
CREATE OR REPLACE FUNCTION initialize_npc_relations()
RETURNS TRIGGER AS $$
DECLARE
    v_player_id UUID;
    v_npc_record RECORD;
BEGIN
    -- 해당 세션의 플레이어 조회
    SELECT player_id INTO v_player_id
    FROM player
    WHERE session_id = NEW.session_id
    LIMIT 1;

    IF v_player_id IS NOT NULL THEN
        -- [Logic] 세션 내에 존재하는 모든 NPC와 플레이어 사이의 관계 슬롯 생성
        FOR v_npc_record IN
            SELECT npc_id FROM npc WHERE session_id = NEW.session_id
        LOOP
            INSERT INTO player_npc_relations (
                player_id,
                npc_id,
                affinity_score,
                relation_type,
                created_at
            )
            VALUES (
                v_player_id,
                v_npc_record.npc_id,
                50, -- 기본 호감도
                'neutral',
                NEW.started_at
            ) ON CONFLICT (player_id, npc_id) DO NOTHING;
        END LOOP;

        RAISE NOTICE '[NPC Relations] Relationship slots initialized for player % with NPCs in session %',
            v_player_id, NEW.session_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 설정: NPC가 모두 복제된 후에 실행되도록 순서 배치
DROP TRIGGER IF EXISTS trigger_09_initialize_npc_relations ON session;
CREATE TRIGGER trigger_09_initialize_npc_relations
    AFTER INSERT ON session
    FOR EACH ROW
    EXECUTE FUNCTION initialize_npc_relations();
