"""
관계(Relation) Cypher 쿼리 통합 테스트
Phase C: get_relations, relation(update_affinity) 메서드의 Cypher 기반 동작 검증
"""

import pytest

from state_db.graph.cypher_engine import engine


# ====================================================================================
# 1. relation.cypher 테스트 (호감도 업데이트)
# ====================================================================================


@pytest.mark.asyncio
async def test_relation_cypher_creates_new_relation(db_lifecycle):
    """
    relation.cypher가 새로운 RELATION 엣지를 생성하는지 확인
    """
    session_id = "test-session-rel-001"
    player_id = "test-player-rel-001"
    npc_uuid = "test-npc-rel-001"

    # Setup: Player, NPC 노드 생성
    setup_query = """
    CREATE (p:Player {id: $player_id, session_id: $session_id, active: true})
    CREATE (n:NPC {id: $npc_uuid, session_id: $session_id, scenario: 'test', rule: 1, active: true})
    RETURN p.id as pid
    """
    await engine.run_cypher(
        setup_query,
        {
            "player_id": player_id,
            "session_id": session_id,
            "npc_uuid": npc_uuid,
        },
    )

    # relation.cypher 실행
    cypher_path = "src/state_db/Query/CYPHER/relation/relation.cypher"
    params = {
        "player_id": player_id,
        "session_id": session_id,
        "npc_uuid": npc_uuid,
        "scenario": "test",
        "rule": 1,
        "relation_type": "neutral",
        "delta_affinity": 50,
        "turn": 1,
        "meta_json": "{}",
    }

    results = await engine.run_cypher(cypher_path, params)

    # 검증: 호감도가 50으로 설정되어야 함
    assert len(results) > 0
    val = results[0]
    if isinstance(val, dict):
        affinity = val.get("affinity", val.get("value", 0))
        active = val.get("active", True)
    else:
        affinity = val
        active = True

    assert int(str(affinity).strip('"')) == 50
    assert active is True


@pytest.mark.asyncio
async def test_relation_cypher_updates_existing_affinity(db_lifecycle):
    """
    relation.cypher가 기존 호감도에 delta를 더하는지 확인
    """
    session_id = "test-session-rel-002"
    player_id = "test-player-rel-002"
    npc_uuid = "test-npc-rel-002"

    # Setup: Player, NPC + 기존 RELATION 생성 (호감도 50)
    setup_query = """
    CREATE (p:Player {id: $player_id, session_id: $session_id, active: true})
    CREATE (n:NPC {id: $npc_uuid, session_id: $session_id, scenario: 'test', rule: 1, active: true})
    CREATE (p)-[:RELATION {relation_type: 'neutral', affinity: 50, active: true, activated_turn: 0}]->(n)
    RETURN p.id as pid
    """
    await engine.run_cypher(
        setup_query,
        {
            "player_id": player_id,
            "session_id": session_id,
            "npc_uuid": npc_uuid,
        },
    )

    # relation.cypher 실행 (+15)
    cypher_path = "src/state_db/Query/CYPHER/relation/relation.cypher"
    params = {
        "player_id": player_id,
        "session_id": session_id,
        "npc_uuid": npc_uuid,
        "scenario": "test",
        "rule": 1,
        "relation_type": "neutral",
        "delta_affinity": 15,
        "turn": 2,
        "meta_json": "{}",
    }

    results = await engine.run_cypher(cypher_path, params)

    # 검증: 호감도가 65가 되어야 함 (50 + 15)
    assert len(results) > 0
    val = results[0]
    if isinstance(val, dict):
        affinity = val.get("affinity", val.get("value", 0))
    else:
        affinity = val

    assert int(str(affinity).strip('"')) == 65


@pytest.mark.asyncio
async def test_relation_cypher_caps_affinity_at_100(db_lifecycle):
    """
    relation.cypher가 호감도 상한(100)을 적용하는지 확인
    """
    session_id = "test-session-rel-003"
    player_id = "test-player-rel-003"
    npc_uuid = "test-npc-rel-003"

    # Setup: Player, NPC + 기존 RELATION (호감도 90)
    setup_query = """
    CREATE (p:Player {id: $player_id, session_id: $session_id, active: true})
    CREATE (n:NPC {id: $npc_uuid, session_id: $session_id, scenario: 'test', rule: 1, active: true})
    CREATE (p)-[:RELATION {relation_type: 'neutral', affinity: 90, active: true, activated_turn: 0}]->(n)
    RETURN p.id as pid
    """
    await engine.run_cypher(
        setup_query,
        {
            "player_id": player_id,
            "session_id": session_id,
            "npc_uuid": npc_uuid,
        },
    )

    # relation.cypher 실행 (+20 -> 110이 되지만 100으로 제한)
    cypher_path = "src/state_db/Query/CYPHER/relation/relation.cypher"
    params = {
        "player_id": player_id,
        "session_id": session_id,
        "npc_uuid": npc_uuid,
        "scenario": "test",
        "rule": 1,
        "relation_type": "neutral",
        "delta_affinity": 20,
        "turn": 3,
        "meta_json": "{}",
    }

    results = await engine.run_cypher(cypher_path, params)

    # 검증: 호감도가 100으로 제한되어야 함
    assert len(results) > 0
    val = results[0]
    if isinstance(val, dict):
        affinity = val.get("affinity", val.get("value", 0))
    else:
        affinity = val

    assert int(str(affinity).strip('"')) == 100


@pytest.mark.asyncio
async def test_relation_cypher_caps_affinity_at_0(db_lifecycle):
    """
    relation.cypher가 호감도 하한(0)을 적용하는지 확인
    """
    session_id = "test-session-rel-004"
    player_id = "test-player-rel-004"
    npc_uuid = "test-npc-rel-004"

    # Setup: Player, NPC + 기존 RELATION (호감도 10)
    setup_query = """
    CREATE (p:Player {id: $player_id, session_id: $session_id, active: true})
    CREATE (n:NPC {id: $npc_uuid, session_id: $session_id, scenario: 'test', rule: 1, active: true})
    CREATE (p)-[:RELATION {relation_type: 'neutral', affinity: 10, active: true, activated_turn: 0}]->(n)
    RETURN p.id as pid
    """
    await engine.run_cypher(
        setup_query,
        {
            "player_id": player_id,
            "session_id": session_id,
            "npc_uuid": npc_uuid,
        },
    )

    # relation.cypher 실행 (-30 -> -20이 되지만 0으로 제한)
    cypher_path = "src/state_db/Query/CYPHER/relation/relation.cypher"
    params = {
        "player_id": player_id,
        "session_id": session_id,
        "npc_uuid": npc_uuid,
        "scenario": "test",
        "rule": 1,
        "relation_type": "neutral",
        "delta_affinity": -30,
        "turn": 4,
        "meta_json": "{}",
    }

    results = await engine.run_cypher(cypher_path, params)

    # 검증: 호감도가 0으로 제한되어야 함
    assert len(results) > 0
    val = results[0]
    if isinstance(val, dict):
        affinity = val.get("affinity", val.get("value", 0))
    else:
        affinity = val

    assert int(str(affinity).strip('"')) == 0


# ====================================================================================
# 2. get_relations.cypher 테스트 (관계 조회)
# ====================================================================================


@pytest.mark.asyncio
async def test_get_relations_cypher_returns_active_relations(db_lifecycle):
    """
    get_relations.cypher가 활성 관계만 반환하는지 확인
    """
    session_id = "test-session-get-001"
    player_id = "test-player-get-001"
    npc1_uuid = "test-npc-get-001"
    npc2_uuid = "test-npc-get-002"

    # Setup: Player + 2개의 NPC (1개는 active, 1개는 inactive)
    setup_query = """
    CREATE (p:Player {id: $player_id, session_id: $session_id, active: true})
    CREATE (n1:NPC {npc_id: $npc1_uuid, session_id: $session_id, name: 'NPC1', active: true})
    CREATE (n2:NPC {npc_id: $npc2_uuid, session_id: $session_id, name: 'NPC2', active: true})
    CREATE (p)-[:RELATION {affinity: 60, active: true, activated_turn: 1, relation_type: 'friend'}]->(n1)
    CREATE (p)-[:RELATION {affinity: 30, active: false, activated_turn: 1, deactivated_turn: 2, relation_type: 'neutral'}]->(n2)
    RETURN p.id as pid
    """
    await engine.run_cypher(
        setup_query,
        {
            "player_id": player_id,
            "session_id": session_id,
            "npc1_uuid": npc1_uuid,
            "npc2_uuid": npc2_uuid,
        },
    )

    # get_relations.cypher 실행
    cypher_path = "src/state_db/Query/CYPHER/relation/get_relations.cypher"
    params = {
        "player_id": player_id,
        "session_id": session_id,
    }

    results = await engine.run_cypher(cypher_path, params)

    # 검증: 활성 관계(NPC1)만 반환되어야 함
    assert len(results) == 1
    val = results[0]
    if isinstance(val, dict):
        npc_id = val.get("npc_id", val.get("value", ""))
        affinity = val.get("affinity_score", 0)
    else:
        npc_id = val
        affinity = 0

    assert str(npc_id).strip('"') == npc1_uuid
    assert int(str(affinity).strip('"')) == 60
