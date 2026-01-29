-- --------------------------------------------------------------------
-- 전투 돌입 (exploration → combat)
-- 용도: 탐색 중 전투 시작
-- --------------------------------------------------------------------

BEGIN;

-- 1. Phase 변경 (exploration → combat)
SELECT change_phase('session_uuid', 'combat'::phase_type);

-- 2. 적 생성
INSERT INTO enemy (session_id, enemy_id, name, state, tags)
VALUES (
    'session_uuid',
    1,
    'Goblin',
    jsonb_build_object(
        'numeric', jsonb_build_object('HP', 30, 'max_hp', 30, 'ATK', 8, 'DEF', 3),
        'boolean', '{}'::jsonb
    ),
    ARRAY['enemy', 'goblin']::TEXT[]
);

-- 3. Turn 증가 (Phase 전환 자체도 상태 변경)
SELECT advance_turn('session_uuid');

-- 4. Turn 상태 변경 기록
SELECT update_turn_state_changes(
    'session_uuid',
    (SELECT current_turn FROM session WHERE session_id = 'session_uuid'),
    '{"phase_changed": "combat", "enemy_spawned": "Goblin"}'::jsonb,
    'phase_transition'
);

COMMIT;
