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

    def check(self, name, method, path, payload=None, params=None):
        start_time = time.time()
        url = f"{BASE_URL}{path}"
        try:
            if method == "GET":
                resp = requests.get(url, params=params)
            elif method == "POST":
                resp = requests.post(url, json=payload)
            elif method == "PUT":
                resp = requests.put(url, json=payload)
            elif method == "DELETE":
                resp = requests.delete(url)

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
                print(f"  [!] {name} Failed: {res_data}")
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

    def run(self):
        # 1. Inject Scenario
        print("[1] Injecting Scenario...")
        scenario_data = {
            "title": "Full Verification Scenario",
            "npcs": [
                {
                    "scenario_npc_id": str(uuid.uuid4()),
                    "name": "Merchant Kim",
                    "description": "Helper",
                }
            ],
            "enemies": [
                {
                    "scenario_enemy_id": str(uuid.uuid4()),
                    "name": "Wild Wolf",
                    "description": "Fierce",
                }
            ],
            "items": [
                {
                    "item_id": str(uuid.uuid4()),
                    "name": "Basic Sword",
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

        # 2. Session Start
        print("[2] Starting Session...")
        start_data = {"scenario_id": self.scenario_id, "location": "Test Field"}
        res = self.check("Start Session", "POST", "/state/session/start", start_data)
        if res and "data" in res:
            self.session_id = res["data"]["session_id"]
            self.player_id = res["data"]["player_id"]

        # 3. Inquiry Endpoints
        print("[3] Testing Inquiry Endpoints...")
        self.check("List All Sessions", "GET", "/state/sessions")
        self.check("List Active Sessions", "GET", "/state/sessions/active")
        self.check("Get Session Info", "GET", f"/state/session/{self.session_id}")

        if self.player_id:
            self.check("Get Player State", "GET", f"/state/player/{self.player_id}")

        self.check(
            "Get Session Inventory",
            "GET",
            f"/state/session/{self.session_id}/inventory",
        )

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
        print("[4] Testing Update Endpoints...")
        if self.player_id:
            self.check(
                "Update Player HP",
                "PUT",
                f"/state/player/{self.player_id}/hp",
                {"session_id": self.session_id, "hp_change": -10},
            )
            self.check(
                "Update Player Stats",
                "PUT",
                f"/state/player/{self.player_id}/stats",
                {"session_id": self.session_id, "stat_changes": {"STR": 5}},
            )
            self.check(
                "Update Inventory",
                "PUT",
                "/state/inventory/update",
                {"player_id": self.player_id, "item_id": 1, "quantity": 3},
            )

        self.check(
            "Change Phase",
            "PUT",
            f"/state/session/{self.session_id}/phase",
            {"new_phase": "combat"},
        )
        self.check(
            "Change Act", "PUT", f"/state/session/{self.session_id}/act", {"new_act": 2}
        )
        self.check(
            "Change Sequence",
            "PUT",
            f"/state/session/{self.session_id}/sequence",
            {"new_sequence": 3},
        )
        self.check(
            "Update Location",
            "PUT",
            f"/state/session/{self.session_id}/location",
            {"new_location": "Hidden Cave"},
        )

        # 5. Manage Endpoints (Entity Spawn/Remove)
        print("[5] Testing Manage Endpoints...")
        dummy_uuid = str(uuid.uuid4())
        self.check(
            "Spawn Extra NPC",
            "POST",
            f"/state/session/{self.session_id}/npc/spawn",
            {"npc_id": dummy_uuid, "name": "Bonus NPC"},
        )
        self.check(
            "Spawn Extra Enemy",
            "POST",
            f"/state/session/{self.session_id}/enemy/spawn",
            {"enemy_id": dummy_uuid, "name": "Bonus Enemy"},
        )

        # 6. Session Control
        print("[6] Testing Session Control...")
        self.check("Pause Session", "POST", f"/state/session/{self.session_id}/pause")
        self.check("Resume Session", "POST", f"/state/session/{self.session_id}/resume")
        self.check("End Session", "POST", f"/state/session/{self.session_id}/end")

        self.print_summary()


if __name__ == "__main__":
    verifier = APIVerifier()
    verifier.run()
