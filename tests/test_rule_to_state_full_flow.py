import pytest
from uuid import uuid4
from state_db.services.state_service import StateService
from state_db.repositories import SessionRepository, EntityRepository
from state_db.schemas.requests import CommitRequest, CommitUpdate, RelationDiff
from state_db.routers.router_COMMIT import state_commit

@pytest.mark.asyncio
async def test_rule_engine_output_to_state_consistency_flow(db_lifecycle):
    """
    룰엔진의 출력이 GM을 거쳐 State Manager에 최종 반영되고 
    조회되는 전체 흐름 검증 (룰엔진 스키마 준수)
    """
    state_service = StateService()
    session_repo = SessionRepository()
    entity_repo = EntityRepository()
    
    # 0. 초기 데이터 셋업 (시나리오/액트/시퀀스)
    scenario_id = str(uuid4())
    from state_db.infrastructure import run_raw_query
    await run_raw_query("INSERT INTO scenario (scenario_id, title) VALUES ($1, $2)", [scenario_id, "Flow Test"])
    await run_raw_query("INSERT INTO scenario_act (scenario_id, act_id, act_name) VALUES ($1, 'act-1', 'Act 1')", [scenario_id])
    await run_raw_query("INSERT INTO scenario_sequence (scenario_id, sequence_id, sequence_name) VALUES ($1, 'seq-1', 'Seq 1')", [scenario_id])
    
    # 1. 세션 및 엔티티 준비
    session = await session_repo.start(scenario_id, 1, 1, "test_loc")
    session_id = str(session.session_id)
    player_id = str(session.player_id)
    
    spawn_res = await entity_repo.spawn_npc(session_id, {
        "scenario_npc_id": "npc-guard",
        "name": "성문 경비병",
        "hp": 100
    })
    npc_id = spawn_res.id
    # 시퀀스 할당 (스냅샷 필터링 통과를 위해 필수)
    await run_raw_query("UPDATE npc SET assigned_sequence_id = 'seq-1' WHERE npc_id = $1", [npc_id])

    # 2. 룰엔진의 출력 모방 (GM이 가공한 최종 RelationDiff)
    # 룰엔진 dialogue_node.py는 RelationType.FRIENDLY("우호적")를 반환함
    rule_output_relation = RelationDiff(
        cause_entity_id=player_id,
        effect_entity_id=npc_id,
        type="우호적",
        affinity_score=75  # 절대값으로 계산된 호감도
    )
    
    # 3. GM -> State Manager 커밋 수행
    commit_request = CommitRequest(
        turn_id=f"{session_id}:1",
        update=CommitUpdate(
            diffs=[],
            relations=[rule_output_relation]
        )
    )
    
    # 실제 라우터 진입점 호출
    commit_response = await state_commit(commit_request, state_service)
    assert commit_response["status"] == "success"

    # 4. 상태 조회 및 데이터 정합성 검증
    snapshot = await state_service.get_state_snapshot(session_id)
    
    # 4-1. 전역 관계 리스트 검증
    found_in_all = False
    for rel in snapshot["relations"]:
        if str(rel.from_id) == player_id and str(rel.to_id) == npc_id:
            assert rel.relation_type == "우호적"
            assert rel.affinity == 75
            found_in_all = True
            break
    assert found_in_all, "Graph DB에 관계가 생성되지 않았습니다."

    # 4-2. 플레이어 중심 관계 데이터(player_relations) 검증
    # GM이 룰엔진에 보낼 때 주로 사용하는 데이터 소스
    player_rels = snapshot["player_relations"]
    assert len(player_rels) > 0
    target_rel = next((r for r in player_rels if str(r.get("id")) == npc_id), None)
    
    assert target_rel is not None
    assert target_rel["relation_type"] == "우호적"
    assert target_rel["affinity"] == 75
    assert target_rel["name"] == "성문 경비병"

    print("\n[SUCCESS] 룰엔진 출력 -> GM 커밋 -> 상태 조회 흐름의 정합성이 확인되었습니다.")
