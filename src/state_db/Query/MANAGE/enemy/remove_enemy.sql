-- --------------------------------------------------------------------
-- remove_enemy.sql
-- Enemy 제거 (물리적 삭제)
-- 용도: 스토리 진행으로 Enemy 퇴장 또는 GM 명령
-- API: DELETE /state/session/{session_id}/enemy/{enemy_instance_id}
-- --------------------------------------------------------------------

-- Enemy 인스턴스 삭제
DELETE FROM enemy
WHERE enemy_id = $1::UUID
  AND session_id = $2::UUID
RETURNING
    enemy_id,
    scenario_enemy_id,
    name,
    description,
    created_at,
    updated_at;

-- 파라미터:
-- $1: enemy_id (UUID)
-- $2: session_id (UUID)
