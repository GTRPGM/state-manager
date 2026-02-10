-- Session 전체 상태 덤프 (디버깅용)
-- 용도: 문제 발생 시 전체 상태 확인
-- API: GET /debug/session/{session_id}/dump

-- Session 기본 정보
SELECT * FROM session WHERE session_id = $1;

-- 연결된 Player
SELECT * FROM player WHERE session_id = $1;

-- Inventory
SELECT pi.*, p.player_id
FROM player_inventory pi
JOIN player p ON pi.player_id = p.player_id
WHERE p.session_id = $1;

-- NPC Relations
SELECT pnr.*, p.player_id
FROM player_npc_relations pnr
JOIN player p ON pnr.player_id = p.player_id
WHERE p.session_id = $1;

-- NPC Instances
SELECT * FROM npc WHERE session_id = $1;

-- Enemy Instances
SELECT * FROM enemy WHERE session_id = $1 AND is_defeated = false;

-- Phase History
SELECT * FROM phase WHERE session_id = $1 ORDER BY transitioned_at;

-- Turn History
SELECT * FROM turn WHERE session_id = $1 ORDER BY turn_number;
