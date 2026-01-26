-- --------------------------------------------------------------------
-- remove_npc.sql
-- NPC 제거 (물리적 삭제)
-- 용도: 스토리 진행으로 NPC 퇴장 또는 GM 명령
-- API: DELETE /state/npc/{npc_instance_id}
-- --------------------------------------------------------------------

-- NPC 인스턴스 삭제
DELETE FROM npc
WHERE npc_instance_id = $1
  AND session_id = $2
RETURNING
    npc_instance_id,
    npc_id,
    name,
    description,
    created_at,
    updated_at;

-- 파라미터:
-- $1: npc_instance_id (UUID)
-- $2: session_id (UUID)

-- 결과 예:
-- npc_instance_id | npc_id | name         | description
-- ----------------|--------|--------------|----------------------
-- uuid-456        | 5      | Merchant Tom | A friendly merchant

-- 주의:
-- - CASCADE 관계가 있다면 관련 데이터도 함께 삭제됨
--   (예: player_npc_relations에 ON DELETE CASCADE 설정 시)
-- - 물리적 삭제이므로 복구 불가능
-- - 중요한 NPC는 soft delete 권장

-- 사용 예:
-- 스토리상 NPC가 떠날 때
-- 테스트 데이터 정리
-- GM이 동적으로 NPC 제거
