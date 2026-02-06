import os
import time
from dataclasses import dataclass
from typing import Any, Callable

import requests

BASE_URL = os.getenv("STATE_MANAGER_BASE_URL", "http://localhost:8030")


@dataclass
class CheckResult:
    name: str
    method: str
    path: str
    status: str
    code: int
    ms: float
    detail: str = ""


class APIVerifier:
    def __init__(self):
        self.results: list[CheckResult] = []
        self.failed: list[str] = []

        self.scenario_id: str | None = None
        self.session_id: str | None = None
        self.player_id: str | None = None
        self.npc_id: str | None = None
        self.enemy_id: str | None = None
        self.item_id: str | None = None
        self.spawned_npc_id: str | None = None
        self.spawned_enemy_id: str | None = None

    def _record(
        self,
        *,
        name: str,
        method: str,
        path: str,
        code: int,
        duration_ms: float,
        ok: bool,
        detail: str = "",
    ) -> None:
        status = "PASS" if ok else "FAIL"
        self.results.append(
            CheckResult(
                name=name,
                method=method,
                path=path,
                status=status,
                code=code,
                ms=round(duration_ms, 2),
                detail=detail,
            )
        )
        if not ok:
            self.failed.append(f"{name}: {detail}")

    @staticmethod
    def _assert_wrapped_success(data: dict[str, Any]) -> None:
        if "status" not in data or "data" not in data:
            raise AssertionError("Response is not WrappedResponse")
        if data["status"] != "success":
            raise AssertionError(f"Expected status=success, got {data['status']}")

    @staticmethod
    def _assert_player_contract(data: dict[str, Any]) -> None:
        APIVerifier._assert_wrapped_success(data)
        payload = data["data"]
        if not isinstance(payload, dict):
            raise AssertionError("player payload is not object")

        required_root = {"player", "player_npc_relations"}
        if set(payload.keys()) != required_root:
            raise AssertionError(f"player root keys mismatch: {set(payload.keys())}")

        player = payload["player"]
        if not isinstance(player, dict):
            raise AssertionError("player field is not object")

        required_player = {"hp", "gold", "items"}
        if set(player.keys()) != required_player:
            raise AssertionError(f"player keys mismatch: {set(player.keys())}")

        if not isinstance(player["items"], list):
            raise AssertionError("player.items is not list")

        for item in player["items"]:
            required_item = {
                "item_id",
                "name",
                "description",
                "item_type",
                "meta",
                "is_stackable",
            }
            if set(item.keys()) != required_item:
                raise AssertionError(f"item keys mismatch: {set(item.keys())}")

    @staticmethod
    def _assert_raw_health(data: dict[str, Any]) -> None:
        if "status" not in data:
            raise AssertionError("raw health response missing status")

    @staticmethod
    def _assert_raw_db_health(data: dict[str, Any]) -> None:
        required = {"status", "database"}
        missing = required - set(data.keys())
        if missing:
            raise AssertionError(f"raw db health missing keys: {missing}")

    @staticmethod
    def _assert_list_payload(data: dict[str, Any]) -> None:
        APIVerifier._assert_wrapped_success(data)
        if not isinstance(data["data"], list):
            raise AssertionError("payload is not list")

    @staticmethod
    def _assert_object_payload(data: dict[str, Any], required_keys: set[str]) -> None:
        APIVerifier._assert_wrapped_success(data)
        payload = data["data"]
        if not isinstance(payload, dict):
            raise AssertionError("payload is not object")
        missing = required_keys - set(payload.keys())
        if missing:
            raise AssertionError(f"missing keys: {missing}")

    def check(
        self,
        name: str,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        expected_status: int = 200,
        validator: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any] | None:
        start = time.time()
        url = f"{BASE_URL}{path}"

        try:
            response = requests.request(
                method=method,
                url=url,
                json=payload,
                params=params,
                timeout=10,
            )
            duration = (time.time() - start) * 1000

            parsed: dict[str, Any] | None = None
            detail = ""
            ok = response.status_code == expected_status

            try:
                parsed = response.json()
            except Exception:
                if ok:
                    ok = False
                    detail = "Response is not valid JSON"

            if ok and parsed is not None:
                try:
                    if validator:
                        validator(parsed)
                    else:
                        self._assert_wrapped_success(parsed)
                except Exception as ve:
                    ok = False
                    detail = f"Validation failed: {ve}"

            if not ok and not detail:
                body = response.text[:300]
                detail = (
                    f"Expected {expected_status}, got {response.status_code}. "
                    f"Body: {body}"
                )

            self._record(
                name=name,
                method=method,
                path=path,
                code=response.status_code,
                duration_ms=duration,
                ok=ok,
                detail=detail,
            )

            if not ok:
                print(f"  [FAIL] {name}: {detail}")
            return parsed
        except Exception as e:
            duration = (time.time() - start) * 1000
            self._record(
                name=name,
                method=method,
                path=path,
                code=0,
                duration_ms=duration,
                ok=False,
                detail=f"Request exception: {e}",
            )
            print(f"  [ERROR] {name}: {e}")
            return None

    def print_summary(self) -> None:
        print("\n" + "=" * 110)
        header = (
            f"{'Endpoint Name':<36} | {'Method':<6} | {'Code':<4} | "
            f"{'Status':<6} | {'MS':<8}"
        )
        print(header)
        print("-" * 110)
        for r in self.results:
            line = (
                f"{r.name:<36} | {r.method:<6} | {r.code:<4} | "
                f"{r.status:<6} | {r.ms:<8}"
            )
            print(line)
        print("=" * 110)
        total = len(self.results)
        failed = len([r for r in self.results if r.status != "PASS"])
        print(f"Total: {total}, Passed: {total - failed}, Failed: {failed}")
        if self.failed:
            print("\nFailures:")
            for f in self.failed:
                print(f"- {f}")

    def _build_scenario_payload(self, legacy_item_id: bool = False) -> dict[str, Any]:
        now = int(time.time())
        item_payload: dict[str, Any] = {
            "scenario_item_id": "item-potion",
            "name": "Healing Potion",
            "rule_id": 1,
            "item_type": "consumable",
            "meta": {"hp_heal": 20, "is_stackable": True},
        }
        if legacy_item_id:
            item_payload["item_id"] = "item-potion"

        return {
            "title": f"Full Verification {now}",
            "description": "Comprehensive endpoint verification",
            "acts": [
                {
                    "id": "act-1",
                    "name": "Act 1",
                    "sequences": ["seq-1"],
                }
            ],
            "sequences": [
                {
                    "id": "seq-1",
                    "name": "Seq 1",
                    "location_name": "Testing Grounds",
                    "npcs": ["npc-1"],
                    "enemies": ["enemy-1"],
                    "items": ["item-potion"],
                }
            ],
            "npcs": [
                {
                    "scenario_npc_id": "npc-1",
                    "name": "Merchant",
                    "rule_id": 101,
                    "description": "A test merchant",
                    "tags": ["friendly"],
                    "state": {"numeric": {"HP": 80}},
                }
            ],
            "enemies": [
                {
                    "scenario_enemy_id": "enemy-1",
                    "name": "Goblin",
                    "rule_id": 201,
                    "description": "A test goblin",
                    "tags": ["hostile"],
                    "state": {"numeric": {"HP": 30, "attack": 10, "defense": 5}},
                }
            ],
            "items": [item_payload],
            "relations": [
                {
                    "from_id": "npc-1",
                    "to_id": "enemy-1",
                    "relation_type": "hostile",
                    "affinity": -50,
                }
            ],
        }

    def run(self) -> int:
        print("[0] Health Checks")
        self.check("Root Health", "GET", "/health", validator=self._assert_raw_health)
        self.check(
            "DB Health", "GET", "/health/db", validator=self._assert_raw_db_health
        )
        self.check(
            "Proxy Health",
            "GET",
            "/state/health/proxy",
            validator=lambda d: self._assert_object_payload(d, {"status", "services"}),
        )
        self.check(
            "Rule Engine Health",
            "GET",
            "/state/health/proxy/rule-engine",
            validator=lambda d: self._assert_object_payload(d, {"connected"}),
        )
        self.check(
            "GM Health",
            "GET",
            "/state/health/proxy/gm",
            validator=lambda d: self._assert_object_payload(d, {"connected"}),
        )

        print("[1] Scenario Endpoints")
        scenario_payload = self._build_scenario_payload()

        self.check(
            "Scenario Validate",
            "POST",
            "/state/scenario/validate",
            payload=scenario_payload,
            validator=lambda d: self._assert_object_payload(d, {"is_valid"}),
        )

        injected = self.check(
            "Scenario Inject",
            "POST",
            "/state/scenario/inject",
            payload=scenario_payload,
            validator=lambda d: self._assert_object_payload(
                d, {"scenario_id", "title"}
            ),
        )
        if injected and injected.get("data"):
            self.scenario_id = injected["data"].get("scenario_id")
        if not self.scenario_id:
            # 일부 배포는 item_id를 요구하는 구형 스키마를 사용한다.
            injected_legacy = self.check(
                "Scenario Inject (legacy-item-id)",
                "POST",
                "/state/scenario/inject",
                payload=self._build_scenario_payload(legacy_item_id=True),
                validator=lambda d: self._assert_object_payload(
                    d, {"scenario_id", "title"}
                ),
            )
            if injected_legacy and injected_legacy.get("data"):
                self.scenario_id = injected_legacy["data"].get("scenario_id")

        self.check(
            "Scenario List (legacy)",
            "GET",
            "/state/scenarios",
            validator=self._assert_list_payload,
        )
        if not self.scenario_id:
            listed = self.check(
                "Scenario List (fallback)",
                "GET",
                "/state/scenarios",
                validator=self._assert_list_payload,
            )
            if listed and listed.get("data"):
                if listed["data"]:
                    self.scenario_id = listed["data"][0].get("scenario_id")
        self.check(
            "Scenario List",
            "GET",
            "/state/scenario/list",
            validator=self._assert_list_payload,
        )
        if self.scenario_id:
            self.check(
                "Scenario Detail",
                "GET",
                f"/state/scenario/{self.scenario_id}",
                validator=lambda d: self._assert_object_payload(
                    d, {"scenario_id", "title"}
                ),
            )

        print("[2] Session & Inquiry")
        if not self.scenario_id:
            print("  [FAIL] Scenario not created; skipping remaining steps.")
            self.print_summary()
            return 1

        started = self.check(
            "Session Start",
            "POST",
            "/state/session/start",
            payload={"scenario_id": self.scenario_id, "location": "Testing Grounds"},
            validator=lambda d: self._assert_object_payload(
                d, {"session_id", "scenario_id", "player_id"}
            ),
        )
        if started and started.get("data"):
            self.session_id = started["data"].get("session_id")
            self.player_id = started["data"].get("player_id")

        if not self.session_id:
            print("  [FAIL] Session not created; skipping remaining steps.")
            self.print_summary()
            return 1

        self.check(
            "Sessions", "GET", "/state/sessions", validator=self._assert_list_payload
        )
        self.check(
            "Active Sessions",
            "GET",
            "/state/sessions/active",
            validator=self._assert_list_payload,
        )
        self.check(
            "Session Detail",
            "GET",
            f"/state/session/{self.session_id}",
            validator=lambda d: self._assert_object_payload(
                d, {"session_id", "scenario_id", "current_turn"}
            ),
        )

        self.check(
            "Session Context",
            "GET",
            f"/state/session/{self.session_id}/context",
            validator=lambda d: self._assert_object_payload(
                d, {"session", "player", "inventory", "relations", "context_scope"}
            ),
        )
        self.check(
            "Session Context (sequence)",
            "GET",
            f"/state/session/{self.session_id}/context",
            params={"sequence_id": "seq-1", "include_inactive": "false"},
            validator=lambda d: self._assert_object_payload(
                d, {"context_scope", "session"}
            ),
        )
        self.check(
            "Progress",
            "GET",
            f"/state/session/{self.session_id}/progress",
            validator=self._assert_wrapped_success,
        )
        self.check(
            "Inventory",
            "GET",
            f"/state/session/{self.session_id}/inventory",
            validator=self._assert_list_payload,
        )
        item_data = self.check(
            "Items",
            "GET",
            f"/state/session/{self.session_id}/items",
            validator=self._assert_list_payload,
        )
        if item_data and isinstance(item_data.get("data"), list):
            items = item_data["data"]
            if items:
                self.item_id = items[0].get("item_id")

        npcs = self.check(
            "NPCs",
            "GET",
            f"/state/session/{self.session_id}/npcs",
            validator=self._assert_list_payload,
        )
        if npcs and npcs.get("data"):
            if npcs["data"]:
                self.npc_id = npcs["data"][0].get("npc_id")

        enemies = self.check(
            "Enemies",
            "GET",
            f"/state/session/{self.session_id}/enemies",
            validator=self._assert_list_payload,
        )
        if enemies and enemies.get("data"):
            if enemies["data"]:
                self.enemy_id = enemies["data"][0].get("enemy_id")

        if self.player_id:
            self.check(
                "Player State",
                "GET",
                f"/state/player/{self.player_id}",
                validator=self._assert_player_contract,
            )

        print("[3] Session Progress Endpoints")
        self.check(
            "Update Location",
            "PUT",
            f"/state/session/{self.session_id}/location",
            payload={"new_location": "Dark Cave"},
            validator=lambda d: self._assert_object_payload(
                d, {"session_id", "location"}
            ),
        )
        self.check(
            "Add Turn",
            "POST",
            f"/state/session/{self.session_id}/turn/add",
            validator=lambda d: self._assert_object_payload(
                d, {"session_id", "current_turn"}
            ),
        )
        self.check(
            "Get Turn",
            "GET",
            f"/state/session/{self.session_id}/turn",
            validator=lambda d: self._assert_object_payload(
                d, {"session_id", "current_turn"}
            ),
        )
        self.check(
            "Change Act",
            "PUT",
            f"/state/session/{self.session_id}/act",
            payload={"new_act": 1, "new_act_id": "act-1", "new_sequence_id": "seq-1"},
            validator=lambda d: self._assert_object_payload(
                d, {"session_id", "current_act", "current_act_id"}
            ),
        )
        self.check(
            "Change Sequence",
            "PUT",
            f"/state/session/{self.session_id}/sequence",
            payload={"new_sequence": 1, "new_sequence_id": "seq-1"},
            validator=lambda d: self._assert_object_payload(
                d, {"session_id", "current_sequence", "current_sequence_id"}
            ),
        )
        self.check(
            "Sequence Details",
            "GET",
            f"/state/session/{self.session_id}/sequence/details",
            validator=lambda d: self._assert_object_payload(
                d, {"sequence_id", "npcs", "enemies", "entity_relations"}
            ),
        )

        print("[4] Update Endpoints")
        if self.player_id:
            self.check(
                "Update Player HP",
                "PUT",
                f"/state/player/{self.player_id}/hp",
                payload={
                    "session_id": self.session_id,
                    "hp_change": -10,
                    "reason": "combat",
                },
                validator=lambda d: self._assert_object_payload(
                    d, {"player_id", "current_hp"}
                ),
            )
            self.check(
                "Update Player Stats",
                "PUT",
                f"/state/player/{self.player_id}/stats",
                payload={"session_id": self.session_id, "stat_changes": {"STR": 1}},
                validator=self._assert_wrapped_success,
            )
            self.check(
                "Inventory Update",
                "PUT",
                "/state/inventory/update",
                payload={"player_id": self.player_id, "rule_id": 1, "quantity": 1},
                validator=self._assert_wrapped_success,
            )
            self.check(
                "Item Earn",
                "POST",
                "/state/player/item/earn",
                payload={
                    "session_id": self.session_id,
                    "player_id": self.player_id,
                    "state_entity_id": self.item_id,
                    "quantity": 2,
                },
                validator=self._assert_wrapped_success,
            )
            self.check(
                "Item Use",
                "POST",
                "/state/player/item/use",
                payload={
                    "session_id": self.session_id,
                    "player_id": self.player_id,
                    "state_entity_id": self.item_id,
                    "quantity": 1,
                },
                validator=self._assert_wrapped_success,
            )

        if self.npc_id and self.player_id:
            self.check(
                "NPC Affinity",
                "PUT",
                "/state/npc/affinity",
                payload={
                    "session_id": self.session_id,
                    "player_id": self.player_id,
                    "npc_id": self.npc_id,
                    "affinity_change": 5,
                    "relation_type": "neutral",
                },
                validator=lambda d: self._assert_object_payload(
                    d, {"player_id", "npc_id", "new_affinity"}
                ),
            )

        if self.enemy_id:
            self.check(
                "Enemy HP",
                "PUT",
                f"/state/enemy/{self.enemy_id}/hp",
                payload={"session_id": self.session_id, "hp_change": -5},
                validator=lambda d: self._assert_object_payload(
                    d, {"enemy_id", "current_hp"}
                ),
            )

        print("[5] Manage Endpoints")
        spawn_npc = self.check(
            "Spawn NPC",
            "POST",
            f"/state/session/{self.session_id}/npc/spawn",
            payload={
                "scenario_npc_id": "npc-dyn-1",
                "rule_id": 102,
                "name": "Dynamic NPC",
                "description": "Spawned during verification",
                "hp": 75,
                "tags": ["dynamic"],
                "state": {},
            },
            validator=lambda d: self._assert_object_payload(d, {"id", "name"}),
        )
        if spawn_npc and spawn_npc.get("data"):
            self.spawned_npc_id = spawn_npc["data"].get("id")

        spawn_enemy = self.check(
            "Spawn Enemy",
            "POST",
            f"/state/session/{self.session_id}/enemy/spawn",
            payload={
                "scenario_enemy_id": "enemy-dyn-1",
                "rule_id": 202,
                "name": "Dynamic Enemy",
                "description": "Spawned during verification",
                "hp": 40,
                "attack": 9,
                "defense": 4,
                "tags": ["dynamic"],
                "state": {},
            },
            validator=lambda d: self._assert_object_payload(d, {"id", "name"}),
        )
        if spawn_enemy and spawn_enemy.get("data"):
            self.spawned_enemy_id = spawn_enemy["data"].get("id")

        if self.spawned_npc_id:
            self.check(
                "Depart NPC",
                "POST",
                f"/state/session/{self.session_id}/npc/{self.spawned_npc_id}/depart",
                validator=lambda d: self._assert_object_payload(
                    d, {"npc_id", "is_departed"}
                ),
            )
            self.check(
                "Return NPC",
                "POST",
                f"/state/session/{self.session_id}/npc/{self.spawned_npc_id}/return",
                validator=lambda d: self._assert_object_payload(
                    d, {"npc_id", "is_departed"}
                ),
            )
            self.check(
                "Remove NPC",
                "DELETE",
                f"/state/session/{self.session_id}/npc/{self.spawned_npc_id}",
                validator=self._assert_wrapped_success,
            )

        if self.spawned_enemy_id:
            self.check(
                "Defeat Enemy",
                "POST",
                f"/state/enemy/{self.spawned_enemy_id}/defeat",
                params={"session_id": self.session_id},
                validator=lambda d: self._assert_object_payload(
                    d, {"enemy_id", "status"}
                ),
            )
            self.check(
                "Remove Enemy",
                "DELETE",
                f"/state/session/{self.session_id}/enemy/{self.spawned_enemy_id}",
                validator=self._assert_wrapped_success,
            )

        print("[6] Commit Endpoint")
        self.check(
            "Commit Wrapped Update",
            "POST",
            "/state/commit",
            payload={
                "turn_id": f"{self.session_id}:1",
                "update": {
                    "diffs": [
                        {
                            "state_entity_id": "player",
                            "diff": {"hp": -1, "location": "commit-zone"},
                        }
                    ],
                    "relations": [],
                },
            },
            validator=lambda d: self._assert_object_payload(
                d, {"commit_id", "updated_fields", "message"}
            ),
        )

        print("[7] Trace Endpoints")
        self.check(
            "Turn History",
            "GET",
            f"/state/session/{self.session_id}/turns",
            validator=self._assert_list_payload,
        )
        self.check(
            "Recent Turns",
            "GET",
            f"/state/session/{self.session_id}/turns/recent",
            params={"limit": 5},
            validator=self._assert_list_payload,
        )
        latest_turn_resp = self.check(
            "Latest Turn",
            "GET",
            f"/state/session/{self.session_id}/turn/latest",
            validator=self._assert_wrapped_success,
        )
        latest_turn_number = None
        if latest_turn_resp and latest_turn_resp.get("data"):
            latest = latest_turn_resp["data"]
            if isinstance(latest, dict):
                latest_turn_number = latest.get("turn_number")
        if latest_turn_number is not None:
            self.check(
                "Turn Details (latest)",
                "GET",
                f"/state/session/{self.session_id}/turn/{latest_turn_number}",
                validator=self._assert_wrapped_success,
            )
        self.check(
            "Turn Range",
            "GET",
            f"/state/session/{self.session_id}/turns/range",
            params={"start": 0, "end": latest_turn_number or 5},
            validator=self._assert_list_payload,
        )
        self.check(
            "Turn Stats By Type",
            "GET",
            f"/state/session/{self.session_id}/turns/statistics/by-type",
            validator=self._assert_list_payload,
        )
        self.check(
            "Turn Duration Analysis",
            "GET",
            f"/state/session/{self.session_id}/turns/duration-analysis",
            validator=self._assert_list_payload,
        )
        self.check(
            "Turn Summary",
            "GET",
            f"/state/session/{self.session_id}/turns/summary",
            validator=self._assert_wrapped_success,
        )

        print("[8] Session Finalization")
        self.check(
            "Pause Session",
            "POST",
            f"/state/session/{self.session_id}/pause",
            validator=self._assert_wrapped_success,
        )
        self.check(
            "Resume Session",
            "POST",
            f"/state/session/{self.session_id}/resume",
            validator=self._assert_wrapped_success,
        )
        self.check(
            "End Session",
            "POST",
            f"/state/session/{self.session_id}/end",
            validator=self._assert_wrapped_success,
        )
        self.check(
            "Delete Session",
            "DELETE",
            f"/state/session/{self.session_id}",
            validator=self._assert_wrapped_success,
        )

        self.print_summary()
        return 1 if self.failed else 0


if __name__ == "__main__":
    raise SystemExit(APIVerifier().run())
