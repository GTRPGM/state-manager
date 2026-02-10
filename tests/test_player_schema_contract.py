from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_player_schema_contract(async_client: AsyncClient):
    payload = {
        "player": {
            "hp": 95,
            "gold": 12,
            "items": [
                {
                    "item_id": "ITEM_POTION_001",
                    "name": "Healing Potion",
                    "description": "Restore HP",
                    "item_type": "consumable",
                    "meta": {"heal_amount": 20},
                    "is_stackable": True,
                }
            ],
        },
        "player_npc_relations": [
            {"npc_id": "npc-1", "npc_name": "Merchant", "affinity_score": 10}
        ],
    }

    with patch(
        "state_db.repositories.PlayerRepository.get_full_state",
        new=AsyncMock(return_value=payload),
    ):
        response = await async_client.get(
            "/state/player/00000000-0000-0000-0000-000000000001"
        )

    assert response.status_code == 200
    data = response.json()["data"]

    assert set(data.keys()) == {"player", "player_npc_relations"}
    assert set(data["player"].keys()) == {"hp", "gold", "items"}
    assert len(data["player"]["items"]) == 1
    assert set(data["player"]["items"][0].keys()) == {
        "item_id",
        "name",
        "description",
        "item_type",
        "meta",
        "is_stackable",
    }


@pytest.mark.asyncio
async def test_player_schema_contract_empty_lists(async_client: AsyncClient):
    payload = {
        "player": {"hp": 100, "gold": 0, "items": []},
        "player_npc_relations": [],
    }

    with patch(
        "state_db.repositories.PlayerRepository.get_full_state",
        new=AsyncMock(return_value=payload),
    ):
        response = await async_client.get(
            "/state/player/00000000-0000-0000-0000-000000000002"
        )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["player"]["items"] == []
    assert data["player_npc_relations"] == []
