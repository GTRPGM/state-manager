import os
import time
from typing import Any
from uuid import uuid4

import requests

BASE_URL = os.getenv("STATE_MANAGER_BASE_URL", "http://localhost:8030")


class FlowError(Exception):
    pass


def req(
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    expected: int = 200,
) -> dict[str, Any]:
    response = requests.request(
        method=method,
        url=f"{BASE_URL}{path}",
        json=payload,
        params=params,
        timeout=20,
    )
    if response.status_code != expected:
        raise FlowError(
            f"{method} {path} failed: expected {expected}, got "
            f"{response.status_code}, body={response.text[:400]}"
        )
    data = response.json()
    if "status" not in data:
        raise FlowError(f"{method} {path} returned invalid WrappedResponse")
    return data


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise FlowError(msg)


def find_by(rows: list[dict[str, Any]], key: str, value: Any) -> dict[str, Any] | None:
    for row in rows:
        if row.get(key) == value:
            return row
    return None


def inject_two_sequence_scenario(max_attempts: int = 3) -> str:
    payload = {
        "title": f"State Guards {time.time_ns()}-{uuid4().hex[:8]}",
        "description": "validate quantity, affinity, sequence scope, session isolation",
        "acts": [
            {
                "id": "act-1",
                "name": "Act 1",
                "sequences": ["seq-1", "seq-2"],
            }
        ],
        "sequences": [
            {
                "id": "seq-1",
                "name": "Village Gate",
                "location_name": "Village",
                "npcs": ["npc-merchant"],
                "enemies": ["enemy-goblin"],
                "items": ["item-potion"],
            },
            {
                "id": "seq-2",
                "name": "Forest Edge",
                "location_name": "Forest",
                "npcs": ["npc-ranger"],
                "enemies": ["enemy-wolf"],
                "items": ["item-potion"],
            },
        ],
        "npcs": [
            {
                "scenario_npc_id": "npc-merchant",
                "name": "Merchant",
                "description": "village trader",
                "rule_id": 101,
                "tags": ["npc"],
                "state": {"numeric": {"HP": 90, "SAN": 10}},
            },
            {
                "scenario_npc_id": "npc-ranger",
                "name": "Ranger",
                "description": "forest guide",
                "rule_id": 102,
                "tags": ["npc"],
                "state": {"numeric": {"HP": 95, "SAN": 10}},
            },
        ],
        "enemies": [
            {
                "scenario_enemy_id": "enemy-goblin",
                "name": "Goblin",
                "description": "small hostile",
                "rule_id": 201,
                "tags": ["enemy"],
                "state": {"numeric": {"HP": 30, "attack": 7, "defense": 3}},
            },
            {
                "scenario_enemy_id": "enemy-wolf",
                "name": "Wolf",
                "description": "pack hunter",
                "rule_id": 202,
                "tags": ["enemy"],
                "state": {"numeric": {"HP": 34, "attack": 9, "defense": 4}},
            },
        ],
        "items": [
            {
                "scenario_item_id": "item-potion",
                "name": "Healing Potion",
                "description": "restore hp",
                "rule_id": 1,
                "item_type": "consumable",
                "meta": {"is_stackable": True},
            }
        ],
        "relations": [
            {
                "from_id": "npc-merchant",
                "to_id": "enemy-goblin",
                "relation_type": "hostile",
                "affinity": -20,
            },
            {
                "from_id": "npc-ranger",
                "to_id": "enemy-wolf",
                "relation_type": "hostile",
                "affinity": -15,
            },
        ],
    }
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            injected = req("POST", "/state/scenario/inject", payload=payload)
            return injected["data"]["scenario_id"]
        except Exception as e:
            last_error = e
            if attempt == max_attempts:
                break
            # 간헐적 그래프 동기화 충돌(500) 완화를 위해 title을 갱신 후 재시도
            payload["title"] = f"State Guards {time.time_ns()}-{uuid4().hex[:8]}"
            time.sleep(0.3)

    raise FlowError(
        f"Scenario inject failed after {max_attempts} attempts: {last_error}"
    )


def start_session(scenario_id: str) -> tuple[str, str]:
    started = req(
        "POST",
        "/state/session/start",
        payload={"scenario_id": scenario_id, "location": "Village"},
    )
    return started["data"]["session_id"], started["data"]["player_id"]


def verify_item_quantity_flow(session_id: str, player_id: str) -> None:
    items = req("GET", f"/state/session/{session_id}/items")["data"]
    assert_true(bool(items), "No item found in session")
    item_id = items[0]["item_id"]

    earn1 = req(
        "POST",
        "/state/player/item/earn",
        payload={
            "session_id": session_id,
            "player_id": player_id,
            "state_entity_id": item_id,
            "quantity": 5,
        },
    )["data"]
    assert_true(earn1["total_quantity"] == 5, "item earn(5) total_quantity mismatch")

    earn2 = req(
        "POST",
        "/state/player/item/earn",
        payload={
            "session_id": session_id,
            "player_id": player_id,
            "state_entity_id": item_id,
            "quantity": 2,
        },
    )["data"]
    assert_true(earn2["total_quantity"] == 7, "item earn(+2) total_quantity mismatch")

    use = req(
        "POST",
        "/state/player/item/use",
        payload={
            "session_id": session_id,
            "player_id": player_id,
            "state_entity_id": item_id,
            "quantity": 3,
        },
    )["data"]
    assert_true(
        use["remaining_quantity"] == 4,
        "item use(-3) remaining_quantity mismatch",
    )

    inventory = req("GET", f"/state/session/{session_id}/inventory")["data"]
    item = find_by(inventory, "item_id", item_id)
    assert_true(item is not None, "item_id inventory row missing after use")
    assert_true(item["quantity"] == 4, "inventory final quantity mismatch")


def verify_affinity_flow(session_id: str, player_id: str) -> None:
    npcs = req("GET", f"/state/session/{session_id}/npcs")["data"]
    assert_true(bool(npcs), "no NPC in session")
    target_npc_id = npcs[0]["npc_id"]

    before_turn = req("GET", f"/state/session/{session_id}/turn")["data"][
        "current_turn"
    ]
    commit_payload = {
        "turn_id": f"{session_id}:{before_turn + 1}",
        "update": {
            "diffs": [
                {
                    "state_entity_id": target_npc_id,
                    "diff": {"affinity": 12},
                }
            ],
            "relations": [],
        },
        "diffs": [],
    }
    req("POST", "/state/commit", payload=commit_payload)

    player_state = req("GET", f"/state/player/{player_id}")["data"]
    rel = find_by(player_state["player_npc_relations"], "npc_id", target_npc_id)
    assert_true(rel is not None, "player-npc relation missing after affinity commit")
    assert_true(rel["affinity_score"] >= 12, "affinity score not updated as expected")


def verify_sequence_scope(session_id: str) -> None:
    seq1 = req(
        "GET",
        f"/state/session/{session_id}/context",
        params={"sequence_id": "seq-1"},
    )["data"]
    seq1_npcs = {n["name"] for n in seq1["npcs"]}
    seq1_enemies = {e["name"] for e in seq1["enemies"]}
    assert_true("Merchant" in seq1_npcs, "seq-1 missing Merchant")
    assert_true("Ranger" not in seq1_npcs, "seq-1 unexpectedly contains Ranger")
    assert_true("Goblin" in seq1_enemies, "seq-1 missing Goblin")
    assert_true("Wolf" not in seq1_enemies, "seq-1 unexpectedly contains Wolf")

    seq2 = req(
        "GET",
        f"/state/session/{session_id}/context",
        params={"sequence_id": "seq-2"},
    )["data"]
    seq2_npcs = {n["name"] for n in seq2["npcs"]}
    seq2_enemies = {e["name"] for e in seq2["enemies"]}
    assert_true("Ranger" in seq2_npcs, "seq-2 missing Ranger")
    assert_true("Merchant" not in seq2_npcs, "seq-2 unexpectedly contains Merchant")
    assert_true("Wolf" in seq2_enemies, "seq-2 missing Wolf")
    assert_true("Goblin" not in seq2_enemies, "seq-2 unexpectedly contains Goblin")


def verify_session_isolation(s1: str, s2: str) -> None:
    s1_enemies = req("GET", f"/state/session/{s1}/enemies")["data"]
    s2_enemies = req("GET", f"/state/session/{s2}/enemies")["data"]
    goblin1 = find_by(s1_enemies, "name", "Goblin")
    goblin2 = find_by(s2_enemies, "name", "Goblin")
    assert_true(
        goblin1 is not None and goblin2 is not None,
        "Goblin not found in both sessions",
    )

    hp2_before = goblin2["current_hp"]
    turn1 = req("GET", f"/state/session/{s1}/turn")["data"]["current_turn"]
    req(
        "POST",
        "/state/commit",
        payload={
            "turn_id": f"{s1}:{turn1 + 1}",
            "update": {
                "diffs": [
                    {
                        "state_entity_id": goblin1["enemy_id"],
                        "diff": {"hp": -8},
                    }
                ],
                "relations": [],
            },
            "diffs": [],
        },
    )

    s1_after = req("GET", f"/state/session/{s1}/enemies")["data"]
    s2_after = req("GET", f"/state/session/{s2}/enemies")["data"]
    goblin1_after = find_by(s1_after, "enemy_id", goblin1["enemy_id"])
    goblin2_after = find_by(s2_after, "enemy_id", goblin2["enemy_id"])
    assert_true(goblin1_after is not None, "session-1 goblin missing after commit")
    assert_true(goblin2_after is not None, "session-2 goblin missing after commit")
    assert_true(
        goblin1_after["current_hp"] == goblin1["current_hp"] - 8,
        "session-1 goblin hp not updated",
    )
    assert_true(
        goblin2_after["current_hp"] == hp2_before,
        "session isolation broken: session-2 goblin hp changed",
    )


def cleanup_session(session_id: str) -> None:
    try:
        req("DELETE", f"/state/session/{session_id}")
    except Exception:
        pass


def run() -> None:
    print("[1/6] Inject scenario with two sequences")
    scenario_id = inject_two_sequence_scenario()

    print("[2/6] Start two sessions for isolation check")
    session_1, player_1 = start_session(scenario_id)
    session_2, _player_2 = start_session(scenario_id)

    try:
        print("[3/6] Verify item quantity add/remove")
        verify_item_quantity_flow(session_1, player_1)

        print("[4/6] Verify affinity update")
        verify_affinity_flow(session_1, player_1)

        print("[5/6] Verify sequence-scoped context")
        verify_sequence_scope(session_1)

        print("[6/6] Verify session-level isolation")
        verify_session_isolation(session_1, session_2)
    finally:
        cleanup_session(session_1)
        cleanup_session(session_2)

    print("SUCCESS: 4-point state checks verified")


if __name__ == "__main__":
    run()
