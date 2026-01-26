-- --------------------------------------------------------------------
-- remove_enemy.sql
-- 적 제거 (물리적 삭제)
-- 용도: 전투 종료 후 적 인스턴스 정리 또는 GM 명령
-- API: DELETE /state/enemy/{enemy_instance_id}
-- --------------------------------------------------------------------

-- 적 인스턴스 삭제
DELETE FROM enemy
WHERE enemy_instance_id = $1
  AND session_id = $2
RETURNING
    enemy_instance_id,
    enemy_id,
    name,
    is_defeated,
    defeated_at;

-- 파라미터:
-- $1: enemy_instance_id (UUID)
-- $2: session_id (UUID)

-- 결과 예:
-- enemy_instance_id | enemy_id | name           | is_defeated | defeated_at
-- ------------------|----------|----------------|-------------|---------------------
-- uuid-abc          | 1        | Goblin Warrior | true        | 2026-01-23 10:30:00

-- 주의:
-- - 보통 is_defeated=true인 적만 삭제
-- - 히스토리 보관이 필요하면 soft delete 사용 (is_defeated만 업데이트)
-- - 이 쿼리는 물리적 삭제이므로 복구 불가능

-- 사용 예:
-- 전투 종료 후 처치된 적 정리
-- GM이 테스트 데이터 정리
