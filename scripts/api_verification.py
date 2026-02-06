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
            print(f"  [ERROR]{name}: {str(e)}")
            return None

    def print_summary(self):
        print("\n" + "=" * 80)
        print(f"{'Endpoint Name':<35} | {'Method':<6} | {'Status':<6} | {'MS':<8}")
        print("-" * 80)
        for r in self.results:
            print(
                f"{r['name']:<35} | {r.get('method', 'N/A'):<6} | "
                f"{r['status']:<6} | {r.get('ms', 0):<8}"
            )
        print("=" * 80 + "\n")

    def run(self):
        print("[0] Checking Health & Proxy...")
        self.check("Rule Engine Health", "GET", "/state/health/proxy/rule-engine")

        print("[1] Scenario Management...")
        scenario_data = {
            "title": f"Full Verification {int(time.time())}",
            "description": "Comprehensive Test",
            "acts": [{"id": "act-1", "name": "Act 1", "sequences": ["seq-1"]}],
            "sequences": [
                {
                    "id": "seq-1",
                    "name": "Seq 1",
                    "location_name": "Testing Grounds",
                    "npcs": ["npc-1"],
                    "enemies": ["enemy-1"],
                }
            ],
            "npcs": [{"scenario_npc_id": "npc-1", "name": "Merchant", "rule_id": 101}],
            "enemies": [
                {"scenario_enemy_id": "enemy-1", "name": "Goblin", "rule_id": 201}
            ],
            "items": [
                {
                    "scenario_item_id": "item-potion",
                    "name": "Healing Potion",
                    "rule_id": 1,
                    "item_type": "consumable",
                    "meta": {"hp_heal": 20},
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
            return

        self.check("Get Scenario List", "GET", "/state/scenarios")
        self.check("Get Scenario Detail", "GET", f"/state/scenario/{self.scenario_id}")

        print("[2] Session Lifecycle...")
        start_data = {"scenario_id": self.scenario_id, "location": "Testing Grounds"}
        res = self.check("Start Session", "POST", "/state/session/start", start_data)
        if res and "data" in res:
            self.session_id = res["data"]["session_id"]
            self.player_id = res["data"].get("player_id")

        self.check("Get Session List", "GET", "/state/sessions")
        self.check("Get Session Detail", "GET", f"/state/session/{self.session_id}")
        self.check("Pause Session", "POST", f"/state/session/{self.session_id}/pause")
        self.check("Resume Session", "POST", f"/state/session/{self.session_id}/resume")

        print("[3] Inquiry (State)...")
        self.check("Get Context", "GET", f"/state/session/{self.session_id}/context")
        self.check("Get Progress", "GET", f"/state/session/{self.session_id}/progress")
        self.check(
            "Get Inventory", "GET", f"/state/session/{self.session_id}/inventory"
        )

        res_npcs = self.check(
            "Get NPCs", "GET", f"/state/session/{self.session_id}/npcs"
        )
        if res_npcs and "data" in res_npcs and res_npcs["data"]:
            self.npc_id = res_npcs["data"][0]["npc_id"]

        res_enemies = self.check(
            "Get Enemies", "GET", f"/state/session/{self.session_id}/enemies"
        )
        if res_enemies and "data" in res_enemies and res_enemies["data"]:
            self.enemy_id = res_enemies["data"][0]["enemy_id"]

        if self.player_id:
            self.check("Get Player State", "GET", f"/state/player/{self.player_id}")

        print("[4] State Updates...")
        if self.player_id:
            self.check(
                "Update Player HP",
                "PUT",
                f"/state/player/{self.player_id}/hp",
                {"session_id": self.session_id, "hp_change": -10},
            )

        if self.npc_id and self.player_id:
            self.check(
                "Update NPC Affinity",
                "PUT",
                "/state/npc/affinity",
                {
                    "session_id": self.session_id,
                    "player_id": self.player_id,
                    "npc_id": self.npc_id,
                    "affinity_change": 5,
                },
            )

        if self.enemy_id:
            self.check(
                "Update Enemy HP",
                "PUT",
                f"/state/enemy/{self.enemy_id}/hp",
                {"session_id": self.session_id, "hp_change": -5},
            )

        if self.player_id:
            self.check(
                "Earn Item",
                "POST",
                "/state/player/item/earn",
                {
                    "session_id": self.session_id,
                    "player_id": self.player_id,
                    "rule_id": 1,
                    "quantity": 2,
                },
            )

        print("[5] Progress Management...")
        self.check(
            "Update Location",
            "PUT",
            f"/state/session/{self.session_id}/location",
            {"new_location": "Dark Cave"},
        )
        self.check("Add Turn", "POST", f"/state/session/{self.session_id}/turn/add")
        self.check("Get Current Turn", "GET", f"/state/session/{self.session_id}/turn")

        self.check(
            "Update Sequence",
            "PUT",
            f"/state/session/{self.session_id}/sequence",
            {"new_sequence": 1, "new_sequence_id": "seq-1"},
        )
        self.check(
            "Get Seq Details",
            "GET",
            f"/state/session/{self.session_id}/sequence/details",
        )

        print("[6] Finalization...")
        self.check("End Session", "POST", f"/state/session/{self.session_id}/end")

        self.print_summary()


if __name__ == "__main__":
    APIVerifier().run()
