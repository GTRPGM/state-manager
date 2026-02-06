import time

import requests

BASE_URL = "http://localhost:8030"


class APIVerifier:
    def __init__(self):
        self.results = []
        self.scenario_id = None
        self.session_id = None
        self.player_id = None
        self.npc_id = None
        self.enemy_id = None

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
            res_data = resp.json() if resp.status_code < 500 else resp.text

            status = "PASS" if resp.status_code < 400 else "FAIL"
            self.results.append(
                {
                    "name": name,
                    "method": method,
                    "path": path,
                    "status": status,
                    "code": resp.status_code,
                    "ms": round(duration, 2),
                }
            )

            if status == "FAIL":
                print(f"  [!]{name} Failed ({resp.status_code}): {res_data}")
            return res_data
        except Exception as e:
            self.results.append({"name": name, "status": "ERROR", "detail": str(e)})
            return None

    def print_summary(self):
        print("\n" + "=" * 80)
        print(f"{'Endpoint Name':<35} | {'Method':<6} | {'Status':<6} | {'MS':<8}")
        print("-" * 80)
        for r in self.results:
            print(
                f"{r['name']:<35} | {r.get('method', 'N/A'):<6} | {r['status']:<6} | {r.get('ms', 0):<8}"
            )
        print("=" * 80 + "\n")

    def run(self):
        # Correct path for proxy health: /state/health/proxy/rule-engine
        print("[0] Checking Proxy Health...")
        self.check("Rule Engine Health", "GET", "/state/health/proxy/rule-engine")

        print("[1] Injecting Scenario...")
        scenario_data = {
            "title": "API Verification",
            "acts": [{"id": "act-1", "name": "Act 1", "sequences": ["seq-1"]}],
            "sequences": [
                {
                    "id": "seq-1",
                    "name": "Seq 1",
                    "npcs": ["npc-1"],
                    "enemies": ["enemy-1"],
                }
            ],
            "npcs": [{"scenario_npc_id": "npc-1", "name": "Merchant", "rule_id": 101}],
            "enemies": [
                {"scenario_enemy_id": "enemy-1", "name": "Goblin", "rule_id": 201}
            ],
            "items": [],
            "relations": [],
        }
        res = self.check(
            "Scenario Injection", "POST", "/state/scenario/inject", scenario_data
        )
        if res and "data" in res:
            self.scenario_id = res["data"]["scenario_id"]
        else:
            return

        print("[2] Session Start...")
        start_data = {"scenario_id": self.scenario_id, "location": "Tavern"}
        res = self.check("Start Session", "POST", "/state/session/start", start_data)
        if res and "data" in res:
            self.session_id = res["data"]["session_id"]
            self.player_id = res["data"].get("player_id")

        print("[3] Inquiry...")
        self.check("Get Context", "GET", f"/state/session/{self.session_id}/context")
        self.check(
            "Get Seq Details",
            "GET",
            f"/state/session/{self.session_id}/sequence/details",
        )

        print("[4] Transition...")
        # Update Sequence (New Schema)
        self.check(
            "Update Sequence",
            "PUT",
            f"/state/session/{self.session_id}/sequence",
            {"new_sequence": 1, "new_sequence_id": "seq-1"},
        )

        print("[5] End...")
        self.check("End Session", "POST", f"/state/session/{self.session_id}/end")
        self.print_summary()


if __name__ == "__main__":
    APIVerifier().run()
