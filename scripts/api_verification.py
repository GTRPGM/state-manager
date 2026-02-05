import time

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
        # 0. Proxy Health Check
        print("[0] Checking Proxy Health...")
        self.check("Rule Engine Health", "GET", "/state/proxy/health/rule-engine")

        # 1. Inject Scenario
        print("[1] Injecting Scenario...")
        scenario_data = {
            "title": "API Verification Scenario",
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
                    "description": "주점입니다.",
                    "exit_triggers": [],
                    "npcs": ["npc-merchant-kim"],
                    "enemies": ["enemy-goblin-1"],
                }
            ],
            "npcs": [
                {
                    "scenario_npc_id": "npc-merchant-kim",
                    "name": "상인 김씨",
                    "state": {"numeric": {"HP": 100}},
                }
            ],
            "enemies": [
                {
                    "scenario_enemy_id": "enemy-goblin-1",
                    "name": "고블린",
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

        # 2. Session Start
        start_data = {"scenario_id": self.scenario_id, "location": "Village Square"}
        res = self.check("Start Session", "POST", "/state/session/start", start_data)
        if res and "data" in res:
            self.session_id = res["data"]["session_id"]
            self.player_id = res["data"].get("player_id")

        # 3. Session Inquiry & Progress
        self.check("List All Sessions", "GET", "/state/sessions")
        self.check("Get Session Info", "GET", f"/state/session/{self.session_id}")
        self.check("Get Progress", "GET", f"/state/session/{self.session_id}/progress")
        self.check(
            "Get Session Context", "GET", f"/state/session/{self.session_id}/context"
        )

        # 4. Player & Entity Actions
        if self.player_id:
            self.check(
                "Update Player HP",
                "PUT",
                f"/state/player/{self.player_id}/hp",
                {"session_id": self.session_id, "hp_change": -5},
            )
            self.check(
                "Earn Item",
                "POST",
                "/state/player/item/earn",
                {
                    "session_id": self.session_id,
                    "player_id": self.player_id,
                    "item_id": 1,
                    "quantity": 1,
                },
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

        # 5. Progress Management
        self.check("Add Turn", "POST", f"/state/session/{self.session_id}/turn/add")
        self.check(
            "Update Location",
            "PUT",
            f"/state/session/{self.session_id}/location",
            {"location": "Tavern Interior"},
        )
        self.check("Get Act", "GET", f"/state/session/{self.session_id}/act")
        self.check("Get Sequence", "GET", f"/state/session/{self.session_id}/sequence")

        # 6. Trace History
        self.check("Get Turn History", "GET", f"/state/session/{self.session_id}/turns")
        self.check(
            "Get Latest Turn", "GET", f"/state/session/{self.session_id}/turn/latest"
        )

        # 7. Session Control
        self.check("Pause Session", "POST", f"/state/session/{self.session_id}/pause")
        self.check("Resume Session", "POST", f"/state/session/{self.session_id}/resume")
        self.check("End Session", "POST", f"/state/session/{self.session_id}/end")

        self.print_summary()


if __name__ == "__main__":
    verifier = APIVerifier()
    verifier.run()
