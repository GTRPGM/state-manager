import pytest
from uuid import uuid4
from state_db.repositories import SessionRepository, EntityRepository, PlayerRepository
from state_db.services.state_service import StateService
from state_db.schemas.requests import CommitRequest, CommitUpdate, RelationDiff

@pytest.mark.asyncio
async def test_relation_creation_and_inquiry_flow(db_lifecycle):
    """
    Test 1: 플레이어-NPC 관계 생성 및 조회 통합 테스트
    1. 세션 생성
    2. NPC 스폰 (SQL -> Graph 트리거 작동 확인)
    3. 관계(Relation) 커밋
    4. 스냅샷 조회를 통한 관계 확인
    """
    session_repo = SessionRepository()
    entity_repo = EntityRepository()
    player_repo = PlayerRepository()
    state_service = StateService()

    # 0. 시나리오 데이터
    scenario_id = str(uuid4())
    from state_db.infrastructure import run_raw_query
    await run_raw_query(
        "INSERT INTO scenario (scenario_id, title) VALUES ($1, $2)",
        [scenario_id, "Test Scenario"]
    )
    # Act 및 Sequence 추가
    await run_raw_query(
        "INSERT INTO scenario_act (scenario_id, act_id, act_name) VALUES ($1, $2, $3)",
        [scenario_id, "act-1", "Act 1"]
    )
    await run_raw_query(
        "INSERT INTO scenario_sequence (scenario_id, sequence_id, sequence_name) VALUES ($1, $2, $3)",
        [scenario_id, "seq-1", "Sequence 1"]
    )

    # 1. 세션 생성
    session = await session_repo.start(scenario_id, 1, 1, "test_loc")
    session_id = str(session.session_id)
    player_id = str(session.player_id)

    # 2. NPC 스폰 및 시퀀스 할당
    # SQL에 INSERT하면 트리거가 Graph 노드를 만들어야 함
    spawn_res = await entity_repo.spawn_npc(session_id, {
        "scenario_npc_id": "npc-test-1",
        "name": "Test NPC",
        "hp": 100
    })
    npc_id = spawn_res.id
    
    # NPC를 현재 시퀀스에 할당
    await run_raw_query(
        "UPDATE npc SET assigned_sequence_id = 'seq-1' WHERE npc_id = $1",
        [npc_id]
    )

    # 3. 관계 커밋
    changes = {
        "player_id": player_id,
        "relation_updates": [
            {
                "cause_entity_id": player_id,
                "effect_entity_id": npc_id,
                "type": "friendly",
                "affinity_score": 75,
                "quantity": None
            }
        ]
    }
    await state_service.write_state_changes(session_id, changes)

    # 4. 조회 및 검증
    snapshot = await state_service.get_state_snapshot(session_id)
    
    # 4-1. NPC 존재 확인
    assert any(str(npc.get("npc_id") or npc.get("id")) == npc_id for npc in snapshot["npcs"])
    
    # 4-2. 관계 존재 확인 (relations 필드)
    relations = snapshot["relations"]
    found = False
    for rel in relations:
        if str(rel.from_id) == player_id and str(rel.to_id) == npc_id:
            assert rel.relation_type == "friendly"
            assert rel.affinity == 75
            found = True
            break
    
    assert found, f"Relation not found between {player_id} and {npc_id}"
    
    # 4-3. player_relations (Cypher 기반 특화 조회) 확인
    player_rels = snapshot["player_relations"]
    assert len(player_rels) > 0
    # context.cypher는 'id', 'affinity' 필드를 사용함
    assert any(str(r.get("id", "")) == npc_id and r.get("affinity") == 75 for r in player_rels)
