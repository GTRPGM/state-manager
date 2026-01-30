import time
import uuid

import requests

BASE_URL = "http://localhost:8030"


class APIVerifier:
    def __init__(self):
        self.results = []
        self.scenario_id = None
        self.session_id = None
        self.player_id = None
        self.npc_instance_id = None
        self.enemy_instance_id = None
        self.null_fields = []

    def find_nulls(self, data, path=""):
        if isinstance(data, dict):
            for k, v in data.items():
                new_path = f"{path}.{k}" if path else k
                if v is None:
                    self.null_fields.append(new_path)
                else:
                    self.find_nulls(v, new_path)
        elif isinstance(data, list):
            for i, v in enumerate(data):
                new_path = f"{path}[{i}]"
                self.find_nulls(v, new_path)

    def check(self, name, method, path, payload=None, params=None):
        start_time = time.time()
        url = f"{BASE_URL}{path}"
        try:
            if method == "GET":
                resp = requests.get(url, params=params)
            elif method == "POST":
                resp = requests.post(url, json=payload, params=params)
            elif method == "PUT":
                resp = requests.put(url, json=payload, params=params)
            elif method == "DELETE":
                resp = requests.delete(url, params=params)

            duration = (time.time() - start_time) * 1000

            res_data = None
            try:
                res_data = resp.json()
            except Exception:
                res_data = resp.text

            # Check both HTTP code and business status field
            status = "PASS"
            if resp.status_code >= 400:
                status = "FAIL"
            elif isinstance(res_data, dict) and res_data.get("status") == "error":
                status = "FAIL"

            self.results.append(
                {
                    "name": name,
                    "method": method,
                    "path": path,
                    "status": status,
                    "code": resp.status_code,
                    "ms": round(duration, 2),
                    "data": res_data,
                }
            )
            if status == "FAIL":
                print(f"  [!]{name} Failed: {res_data}")

            # Null Check
            if isinstance(res_data, dict) and "data" in res_data:
                self.find_nulls(res_data["data"], f"{name}:data")

            return res_data
        except Exception as e:
            self.results.append(
                {
                    "name": name,
                    "method": method,
                    "path": path,
                    "status": "ERROR",
                    "detail": str(e),
                }
            )
            return None

    def print_summary(self):
        print("\n" + "=" * 80)
        print(f"{'Endpoint Name':<35} | {'Method':<6} | {'Status':<6} | {'MS':<8}")
        print("-" * 80)
        for r in self.results:
            name = r["name"]
            method = r.get("method", "N/A")
            status = r["status"]
            ms = r.get("ms", 0)
            print(f"{name:<35} | {method:<6} | {status:<6} | {ms:<8}")
        print("=" * 80 + "\n")

        if self.null_fields:
            print("\n[WARNING] Found NULL values in responses:")
            for field in self.null_fields:
                print(f" - {field}")
        else:
            print("\n[OK] No NULL values found in responses.")

    def run(self):
        # 1. Inject Scenario
        print("[1] Injecting Scenario...")
        scenario_data = {
            "title": "Full API Verification Scenario",
            "acts": [
                {
                    "id": "act-1",
                    "name": "시작의 마을",
                    "description": "평화로운 마을에서 시작합니다.",
                    "sequences": ["seq-tavern"],
                }
            ],
            "sequences": [
                {
                    "id": "seq-tavern",
                    "name": "주점 대화",
                    "location_name": "광장 주점",
                    "description": "술 냄새가 진동하는 주점입니다.",
                    "exit_triggers": ["NPC와 대화 완료"],
                    "npcs": ["npc-merchant-kim"],
                    "enemies": ["enemy-goblin-1"],
                    "items": ["item-basic-sword"],
                }
            ],
            "npcs": [
                {
                    "scenario_npc_id": "npc-merchant-kim",
                    "name": "상인 김씨",
                    "description": "물건을 파는 상인입니다.",
                    "state": {"numeric": {"HP": 100, "affinity": 50}},
                }
            ],
            "enemies": [
                {
                    "scenario_enemy_id": "enemy-goblin-1",
                    "name": "고블린",
                    "description": "약해 보이는 고블린입니다.",
                    "state": {"numeric": {"HP": 30}},
                }
            ],
            "items": [
                {
                    "item_id": 1,
                    "name": "녹슨 칼",
                    "item_type": "equipment",
                }
            ],
            "relations": [],
        }
        res = self.check(
            "Scenario Injection", "POST", "/state/scenario/inject", scenario_data
        )
        if res and "data" in res:
            self.scenario_id = res["data"]["scenario_id"]
        else:
            print("  [! ] Failed to inject scenario")
            return

        # 1.1 Scenario Inquiry
        self.check("List Scenarios", "GET", "/state/scenarios")
        self.check("Get Scenario Detail", "GET", f"/state/scenario/{self.scenario_id}")

        # 2. Session Start
        start_data = {"scenario_id": self.scenario_id, "location": "Village Square"}
        res = self.check("Start Session", "POST", "/state/session/start", start_data)
        if res and "data" in res:
            self.session_id = res["data"]["session_id"]
            self.player_id = res["data"].get("player_id")
            if not self.player_id:
                s_info = self.check(
                    "Get Session Info", "GET", f"/state/session/{self.session_id}"
                )
                if s_info and "data" in s_info:
                    self.player_id = s_info["data"].get("player_id")

        # 3. Inquiry Endpoints
        self.check("List All Sessions", "GET", "/state/sessions")
        self.check("List Active Sessions", "GET", "/state/sessions/active")

        if self.player_id:
            self.check("Get Player State", "GET", f"/state/player/{self.player_id}")

        self.check(
            "Get Session Inventory",
            "GET",
            f"/state/session/{self.session_id}/inventory",
        )

        # Get real Item UUID from session/scenario
        item_uuid = None
        # Use the new items endpoint to find all available items in the session
        items_res = self.check(
            "List Session Items", "GET", f"/state/session/{self.session_id}/items"
        )
        if items_res and items_res.get("data"):
            # Use the first item available in the session
            item_uuid = items_res["data"][0].get("item_id")

        if not item_uuid:
            item_uuid = str(uuid.uuid4())

        res = self.check(
            "Get Session NPCs", "GET", f"/state/session/{self.session_id}/npcs"
        )
        if res and res.get("data"):
            self.npc_instance_id = res["data"][0]["npc_id"]

        res = self.check(
            "Get Session Enemies", "GET", f"/state/session/{self.session_id}/enemies"
        )
        if res and res.get("data"):
            self.enemy_instance_id = res["data"][0]["enemy_instance_id"]

        # 4. Update Endpoints
        if self.player_id:
            self.check(
                "Update Player HP",
                "PUT",
                f"/state/player/{self.player_id}/hp",
                {"session_id": self.session_id, "hp_change": -5},
            )
            self.check(
                "Update Player Stats",
                "PUT",
                f"/state/player/{self.player_id}/stats",
                {"session_id": self.session_id, "stat_changes": {"INT": 2}},
            )
            self.check(
                "Update Inventory",
                "PUT",
                "/state/inventory/update",
                {"player_id": self.player_id, "item_id": item_uuid, "quantity": 5},
            )
            self.check(
                "Earn Item",
                "POST",
                "/state/player/item/earn",
                {
                    "session_id": self.session_id,
                    "player_id": self.player_id,
                    "item_id": item_uuid,
                    "quantity": 1,
                },
            )
            self.check(
                "Use Item",
                "POST",
                "/state/player/item/use",
                {
                    "session_id": self.session_id,
                    "player_id": self.player_id,
                    "item_id": item_uuid,
                    "quantity": 1,
                },
            )
            if self.npc_instance_id:
                self.check(
                    "Update NPC Affinity",
                    "PUT",
                    "/state/npc/affinity",
                    {
                        "player_id": self.player_id,
                        "npc_id": self.npc_instance_id,
                        "affinity_change": 10,
                    },
                )

        if self.enemy_instance_id:
            self.check(
                "Update Enemy HP",
                "PUT",
                f"/state/enemy/{self.enemy_instance_id}/hp",
                {"session_id": self.session_id, "hp_change": -10},
            )
            self.check(
                "Defeat Enemy",
                "POST",
                f"/state/enemy/{self.enemy_instance_id}/defeat",
                params={"session_id": self.session_id},
            )

        self.check(
            "Change Phase",
            "PUT",
            f"/state/session/{self.session_id}/phase",
            {"new_phase": "dialogue"},
        )
        self.check("Add Turn", "POST", f"/state/session/{self.session_id}/turn/add")
        self.check(
            "Update Location",
            "PUT",
            f"/state/session/{self.session_id}/location",
            {"new_location": "Tavern Interior"},
        )

        # New: Act/Sequence Management
        self.check("Get Act", "GET", f"/state/session/{self.session_id}/act")
        self.check("Add Act", "POST", f"/state/session/{self.session_id}/act/add")
        self.check("Back Act", "POST", f"/state/session/{self.session_id}/act/back")
        self.check("Get Sequence", "GET", f"/state/session/{self.session_id}/sequence")
        self.check(
            "Add Sequence", "POST", f"/state/session/{self.session_id}/sequence/add"
        )
        self.check(
            "Back Sequence", "POST", f"/state/session/{self.session_id}/sequence/back"
        )

        # 5. Manage Endpoints
        dummy_uuid = str(uuid.uuid4())
        self.check(
            "Spawn Extra NPC",
            "POST",
            f"/state/session/{self.session_id}/npc/spawn",
            {"npc_id": dummy_uuid, "name": "Traveler"},
        )
        self.check(
            "Spawn Extra Enemy",
            "POST",
            f"/state/session/{self.session_id}/enemy/spawn",
            {"enemy_id": dummy_uuid, "name": "Bat"},
        )

        # 6. Trace Endpoints
        self.check("Get Turn History", "GET", f"/state/session/{self.session_id}/turns")
        self.check(
            "Get Recent Turns",
            "GET",
            f"/state/session/{self.session_id}/turns/recent",
            params={"limit": 5},
        )
        self.check(
            "Get Latest Turn", "GET", f"/state/session/{self.session_id}/turn/latest"
        )
        self.check(
            "Get Turn Range",
            "GET",
            f"/state/session/{self.session_id}/turns/range",
            params={"start": 0, "end": 2},
        )
        self.check(
            "Get Turn Summary", "GET", f"/state/session/{self.session_id}/turns/summary"
        )
        self.check(
            "Get Turn Statistics by Phase",
            "GET",
            f"/state/session/{self.session_id}/turns/statistics/by-phase",
        )
        self.check(
            "Get Turn Duration Analysis",
            "GET",
            f"/state/session/{self.session_id}/turns/duration-analysis",
        )

        self.check(
            "Get Phase History", "GET", f"/state/session/{self.session_id}/phases"
        )
        self.check(
            "Get Latest Phase", "GET", f"/state/session/{self.session_id}/phase/latest"
        )
        self.check(
            "Get Phase Range",
            "GET",
            f"/state/session/{self.session_id}/phases/range",
            params={"start_turn": 0, "end_turn": 5},
        )
        self.check(
            "Get Phase Statistics",
            "GET",
            f"/state/session/{self.session_id}/phases/statistics",
        )
        self.check(
            "Get Phase Pattern",
            "GET",
            f"/state/session/{self.session_id}/phases/pattern",
        )
        self.check(
            "Get Phase Summary",
            "GET",
            f"/state/session/{self.session_id}/phases/summary",
        )

        # 7. Session Control
        self.check("Pause Session", "POST", f"/state/session/{self.session_id}/pause")
        self.check("Resume Session", "POST", f"/state/session/{self.session_id}/resume")
        self.check("End Session", "POST", f"/state/session/{self.session_id}/end")

        self.print_summary()


if __name__ == "__main__":
    verifier = APIVerifier()
    verifier.run()
