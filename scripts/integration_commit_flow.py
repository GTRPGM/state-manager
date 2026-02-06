import os
import sys
import time
from typing import Any

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
    url = f"{BASE_URL}{path}"
    response = requests.request(
        method=method,
        url=url,
        json=payload,
        params=params,
        timeout=15,
    )
    if response.status_code != expected:
        raise FlowError(
            f"{method} {path} failed: expected {expected}, got "
            f"{response.status_code}, body={response.text[:400]}"
        )
    try:
        data = response.json()
    except Exception as e:
        raise FlowError(f"{method} {path} returned non-JSON: {e}") from e

    if "status" not in data:
        raise FlowError(f"{method} {path} is not WrappedResponse")
    return data


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise FlowError(msg)


def find_by_key(
    rows: list[dict[str, Any]],
    key: str,
    value: Any,
) -> dict[str, Any] | None:
    for row in rows:
        if row.get(key) == value:
            return row
    return None


def run_flow() -> None:
    print("[1/7] Inject scenario")
    scenario_payload = {
        "title": f"Commit Integration {int(time.time())}",
        "description": "integration flow for commit verification",
        "acts": [{"id": "act-1", "name": "Act 1", "sequences": ["seq-1"]}],
        "sequences": [
            {
                "id": "seq-1",
                "name": "Start Sequence",
                "location_name": "Town",
                "npcs": ["npc-merchant"],
                "enemies": ["enemy-goblin"],
                "items": ["item-potion"],
            }
        ],
        "npcs": [
            {
                "scenario_npc_id": "npc-merchant",
                "name": "Merchant",
                "description": "friendly npc",
                "rule_id": 101,
                "tags": ["npc"],
                "state": {"numeric": {"HP": 80, "SAN": 10}},
            }
        ],
        "enemies": [
            {
                "scenario_enemy_id": "enemy-goblin",
                "name": "Goblin",
                "description": "hostile enemy",
                "rule_id": 201,
                "tags": ["enemy"],
                "state": {"numeric": {"HP": 30, "attack": 8, "defense": 3}},
            }
        ],
        "items": [
            {
                "scenario_item_id": "item-potion",
                "name": "Healing Potion",
                "description": "heals hp",
                "rule_id": 1,
                "item_type": "consumable",
                "meta": {"heal_amount": 20, "is_stackable": True},
            }
        ],
        "relations": [
            {
                "from_id": "npc-merchant",
                "to_id": "enemy-goblin",
                "relation_type": "hostile",
                "affinity": -20,
            }
        ],
    }

    injected = req("POST", "/state/scenario/inject", payload=scenario_payload)
    scenario_id = injected["data"]["scenario_id"]

    print("[2/7] Start session")
    started = req(
        "POST",
        "/state/session/start",
        payload={"scenario_id": scenario_id, "location": "Town"},
    )
    session_id = started["data"]["session_id"]
    player_id = started["data"]["player_id"]

    print("[3/7] Fetch baseline context")
    before_ctx = req("GET", f"/state/session/{session_id}/context")["data"]
    before_turn = req("GET", f"/state/session/{session_id}/turn")["data"][
        "current_turn"
    ]
    before_player_hp = before_ctx["player"]["hp"]

    npcs = req("GET", f"/state/session/{session_id}/npcs")["data"]
    enemies = req("GET", f"/state/session/{session_id}/enemies")["data"]
    assert_true(bool(npcs), "No NPC found in session")
    assert_true(bool(enemies), "No enemy found in session")

    npc_id = npcs[0]["npc_id"]
    enemy_id = enemies[0]["enemy_id"]
    before_enemy_hp = enemies[0]["current_hp"]

    print("[4/7] Prepare quantity baseline (earn item)")
    req(
        "POST",
        "/state/player/item/earn",
        payload={
            "session_id": session_id,
            "player_id": player_id,
            "rule_id": 1,
            "quantity": 5,
        },
    )

    inventory = req("GET", f"/state/session/{session_id}/inventory")["data"]
    assert_true(bool(inventory), "No inventory item found after earn")
    item_row = find_by_key(inventory, "rule_id", 1)
    assert_true(item_row is not None, "Rule 1 item not found in inventory")
    item_uuid = item_row["item_id"]

    print("[5/7] Commit all entity changes (attributes, relations, quantity)")
    commit_payload = {
        "turn_id": f"{session_id}:{before_turn + 1}",
        "update": {
            "diffs": [
                {
                    "state_entity_id": "player",
                    "diff": {
                        "hp": -7,
                        "san": -1,
                        "stats": {"STR": 1, "DEX": 1},
                        "location": "Old Ruins",
                    },
                },
                {"state_entity_id": npc_id, "diff": {"affinity": 9}},
                {"state_entity_id": enemy_id, "diff": {"hp": -6}},
            ],
            "relations": [
                {
                    "cause_entity_id": player_id,
                    "effect_entity_id": npc_id,
                    "type": "우호적",
                    "affinity_score": 65,
                },
                {
                    "cause_entity_id": npc_id,
                    "effect_entity_id": enemy_id,
                    "type": "적대적",
                    "affinity_score": -90,
                    "quantity": 4,
                },
                {
                    "cause_entity_id": player_id,
                    "effect_entity_id": item_uuid,
                    "type": "소유",
                    "quantity": 4,
                },
            ],
        },
        "diffs": [],
    }
    commit_res = req("POST", "/state/commit", payload=commit_payload)
    assert_true("commit_id" in commit_res["data"], "commit_id missing")

    print("[6/7] Verify post-commit state")
    after_ctx = req("GET", f"/state/session/{session_id}/context")["data"]
    after_turn = req("GET", f"/state/session/{session_id}/turn")["data"]["current_turn"]
    after_session = req("GET", f"/state/session/{session_id}")["data"]
    after_player = req("GET", f"/state/player/{player_id}")["data"]
    after_enemies = req("GET", f"/state/session/{session_id}/enemies")["data"]

    # 속성 변경 검증
    assert_true(
        after_ctx["player"]["hp"] == before_player_hp - 7,
        "player hp not updated",
    )
    assert_true(
        after_session["location"] == "Old Ruins",
        "session location not updated",
    )

    enemy_after = find_by_key(after_enemies, "enemy_id", enemy_id)
    assert_true(enemy_after is not None, "enemy missing after commit")
    assert_true(
        enemy_after["current_hp"] == before_enemy_hp - 6,
        "enemy hp not updated",
    )

    # NPC affinity 변경 검증 (player endpoint)
    rel = find_by_key(after_player["player_npc_relations"], "npc_id", npc_id)
    assert_true(rel is not None, "player-npc relation missing after commit")
    assert_true(rel["affinity_score"] >= 9, "npc affinity not updated")

    # 관계/수량 변경 검증 (context.relations)
    relations = after_ctx["relations"]
    rel_npc_enemy = None
    for r in relations:
        if (
            r.get("from_id") == npc_id
            and r.get("to_id") == enemy_id
            and r.get("relation_type") == "적대적"
        ):
            rel_npc_enemy = r

    assert_true(
        rel_npc_enemy is not None,
        f"npc->enemy relation not found. relation_count={len(relations)}",
    )
    assert_true(
        rel_npc_enemy.get("affinity") == -90,
        "npc->enemy affinity mismatch",
    )
    assert_true(
        rel_npc_enemy.get("quantity") == 4,
        "npc->enemy quantity mismatch",
    )

    # 턴 증가 검증
    assert_true(after_turn == before_turn + 1, "turn did not increment")

    print("[7/7] Cleanup")
    req("POST", f"/state/session/{session_id}/end")
    req("DELETE", f"/state/session/{session_id}")

    print("SUCCESS: integration commit flow verified")


if __name__ == "__main__":
    try:
        run_flow()
    except FlowError as e:
        print(f"FAILED: {e}")
        sys.exit(1)
