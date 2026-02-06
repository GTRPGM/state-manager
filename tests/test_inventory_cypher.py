"""
인벤토리 Cypher 쿼리 통합 테스트
Phase C: earn_item, use_item 메서드의 Cypher 기반 동작 검증
"""

import pytest

from state_db.graph.cypher_engine import engine

# ====================================================================================
# 1. earn_item.cypher 테스트
# ====================================================================================


@pytest.mark.asyncio
async def test_earn_item_cypher_creates_contains_relation(db_lifecycle):
    """
    earn_item.cypher가 CONTAINS 관계를 생성하고 수량을 설정하는지 확인
    """
    session_id = "test-session-earn-001"
    player_id = "test-player-001"
    inventory_id = "test-inventory-001"
    item_uuid = "test-item-001"

    # Setup: Player, Inventory, Item 노드 생성
    setup_query = """
    CREATE (p:Player {id: $player_id, session_id: $session_id, active: true})
    CREATE (inv:Inventory {id: $inventory_id, session_id: $session_id, active: true})
    CREATE (i:Item {
        id: $item_uuid, session_id: $session_id,
        scenario: 'test', rule: 1, active: true
    })
    RETURN p.id as pid
    """
    await engine.run_cypher(
        setup_query,
        {
            "player_id": player_id,
            "session_id": session_id,
            "inventory_id": inventory_id,
            "item_uuid": item_uuid,
        },
    )

    # earn_item.cypher 실행
    cypher_path = "src/state_db/Query/CYPHER/inventory/earn_item.cypher"
    params = {
        "player_id": player_id,
        "session_id": session_id,
        "inventory_id": inventory_id,
        "item_uuid": item_uuid,
        "scenario": "test",
        "rule": 1,
        "delta_qty": 5,
    }

    results = await engine.run_cypher(cypher_path, params)

    # 검증
    assert len(results) > 0
    val = results[0]
    print(f"\nDEBUG: type(val)={type(val)}, val={val}")

    quantity = 0
    if isinstance(val, dict):
        if "quantity" in val:
            quantity = val["quantity"]
        elif "properties" in val:
            quantity = val["properties"].get("quantity", 0)
        elif "value" in val:
            inner = val["value"]
            quantity = inner.get("quantity", 0) if isinstance(inner, dict) else inner
    else:
        quantity = val

    assert int(quantity) == 5


@pytest.mark.asyncio
async def test_earn_item_cypher_adds_to_existing_quantity(db_lifecycle):
    """
    earn_item.cypher가 기존 수량에 추가하는지 확인 (delta 방식)
    """
    session_id = "test-session-earn-002"
    player_id = "test-player-002"
    inventory_id = "test-inventory-002"
    item_uuid = "test-item-002"

    # Setup: Player, Inventory, Item + 기존 CONTAINS 관계 생성
    setup_query = """
    CREATE (p:Player {id: $player_id, session_id: $session_id, active: true})
    CREATE (inv:Inventory {id: $inventory_id, session_id: $session_id, active: true})
    CREATE (i:Item {
        id: $item_uuid, session_id: $session_id,
        scenario: 'test', rule: 1, active: true
    })
    CREATE (inv)-[:CONTAINS {quantity: 10, active: true}]->(i)
    RETURN p.id as pid
    """
    await engine.run_cypher(
        setup_query,
        {
            "player_id": player_id,
            "session_id": session_id,
            "inventory_id": inventory_id,
            "item_uuid": item_uuid,
        },
    )

    # earn_item.cypher 실행 (추가 5개)
    cypher_path = "src/state_db/Query/CYPHER/inventory/earn_item.cypher"
    params = {
        "player_id": player_id,
        "session_id": session_id,
        "inventory_id": inventory_id,
        "item_uuid": item_uuid,
        "scenario": "test",
        "rule": 1,
        "delta_qty": 5,
    }

    results = await engine.run_cypher(cypher_path, params)

    # 검증
    assert len(results) > 0
    val = results[0]

    quantity = 0
    if isinstance(val, dict):
        if "quantity" in val:
            quantity = val["quantity"]
        elif "properties" in val:
            quantity = val["properties"].get("quantity", 0)
        elif "value" in val:
            inner = val["value"]
            quantity = inner.get("quantity", 0) if isinstance(inner, dict) else inner
    else:
        quantity = val

    assert int(quantity) == 15


# ====================================================================================
# 2. use_item.cypher 테스트
# ====================================================================================


@pytest.mark.asyncio
async def test_use_item_cypher_decreases_quantity(db_lifecycle):
    """
    use_item.cypher가 수량을 감소시키는지 확인
    """
    session_id = "test-session-use-001"
    player_id = "test-player-use-001"
    inventory_id = "test-inventory-use-001"
    item_uuid = "test-item-use-001"

    # Setup: Player -> HAS_INVENTORY -> Inventory -> CONTAINS -> Item
    setup_query = """
    CREATE (p:Player {id: $player_id, session_id: $session_id, active: true})
    CREATE (inv:Inventory {id: $inventory_id, session_id: $session_id, active: true})
    CREATE (i:Item {
        id: $item_uuid, session_id: $session_id,
        scenario: 'test', rule: 1, active: true
    })
    CREATE (p)-[:HAS_INVENTORY {active: true}]->(inv)
    CREATE (inv)-[:CONTAINS {quantity: 10, active: true}]->(i)
    RETURN p.id as pid
    """
    await engine.run_cypher(
        setup_query,
        {
            "player_id": player_id,
            "session_id": session_id,
            "inventory_id": inventory_id,
            "item_uuid": item_uuid,
        },
    )

    # use_item.cypher 실행 (3개 사용)
    cypher_path = "src/state_db/Query/CYPHER/inventory/use_item.cypher"
    params = {
        "player_id": player_id,
        "session_id": session_id,
        "inventory_id": inventory_id,
        "item_uuid": item_uuid,
        "scenario": "test",
        "rule": 1,
        "use_qty": 3,
        "turn": 1,
    }

    results = await engine.run_cypher(cypher_path, params)

    # 검증: 수량이 7이 되어야 함 (10 - 3)
    assert len(results) > 0
    val = results[0]

    quantity = 0
    active = False
    if isinstance(val, dict):
        if "quantity" in val:
            quantity = val["quantity"]
            active = val.get("active", True)
        elif "properties" in val:
            quantity = val["properties"].get("quantity", 0)
            active = val["properties"].get("active", True)
        elif "value" in val:
            inner = val["value"]
            if isinstance(inner, dict):
                quantity = inner.get("quantity", 0)
                active = inner.get("active", True)
            else:
                quantity = inner
                active = True
    else:
        quantity = val
        active = True

    assert int(quantity) == 7
    assert active is True


@pytest.mark.asyncio
async def test_use_item_cypher_deactivates_when_zero(db_lifecycle):
    """
    use_item.cypher가 수량이 0 이하가 되면 비활성화하는지 확인
    """
    session_id = "test-session-use-002"
    player_id = "test-player-use-002"
    inventory_id = "test-inventory-use-002"
    item_uuid = "test-item-use-002"

    # Setup: 수량 3개인 아이템
    setup_query = """
    CREATE (p:Player {id: $player_id, session_id: $session_id, active: true})
    CREATE (inv:Inventory {id: $inventory_id, session_id: $session_id, active: true})
    CREATE (i:Item {
        id: $item_uuid, session_id: $session_id,
        scenario: 'test', rule: 1, active: true
    })
    CREATE (p)-[:HAS_INVENTORY {active: true}]->(inv)
    CREATE (inv)-[:CONTAINS {quantity: 3, active: true}]->(i)
    RETURN p.id as pid
    """
    await engine.run_cypher(
        setup_query,
        {
            "player_id": player_id,
            "session_id": session_id,
            "inventory_id": inventory_id,
            "item_uuid": item_uuid,
        },
    )

    # use_item.cypher 실행 (5개 사용 -> 0 이하가 됨)
    cypher_path = "src/state_db/Query/CYPHER/inventory/use_item.cypher"
    params = {
        "player_id": player_id,
        "session_id": session_id,
        "inventory_id": inventory_id,
        "item_uuid": item_uuid,
        "scenario": "test",
        "rule": 1,
        "use_qty": 5,
        "turn": 2,
    }

    results = await engine.run_cypher(cypher_path, params)

    # 검증: 수량이 0이고 비활성화되어야 함
    assert len(results) > 0
    val = results[0]

    quantity = 0
    active = True
    if isinstance(val, dict):
        if "quantity" in val:
            quantity = val["quantity"]
            active = val.get("active", True)
        elif "properties" in val:
            quantity = val["properties"].get("quantity", 0)
            active = val["properties"].get("active", True)
        elif "value" in val:
            inner = val["value"]
            if isinstance(inner, dict):
                quantity = inner.get("quantity", 0)
                active = inner.get("active", True)
            else:
                quantity = inner
                active = True
    else:
        quantity = val
        active = True

    assert int(quantity) == 0
    assert active is False
