from unittest.mock import AsyncMock, patch

import pytest

from state_db.repositories.player import PlayerRepository


@pytest.mark.asyncio
async def test_get_inventory_enriches_item_metadata():
    repo = PlayerRepository()

    with (
        patch.object(
            repo,
            "_get_player_id_by_session",
            new=AsyncMock(return_value="player-1"),
        ),
        patch(
            "state_db.repositories.player.cypher_engine.run_cypher",
            new=AsyncMock(
                return_value=[
                    {
                        "item_id": "11111111-1111-1111-1111-111111111111",
                        "rule_id": 7901,
                        "quantity": 2,
                    }
                ]
            ),
        ),
        patch(
            "state_db.repositories.player.run_raw_query",
            new=AsyncMock(
                return_value=[
                    {
                        "item_id": "11111111-1111-1111-1111-111111111111",
                        "scenario_item_id": "item-healing-potion-1",
                        "name": "회복 포션",
                        "description": "기본 회복용 포션",
                        "item_type": "consumable",
                    }
                ]
            ),
        ),
    ):
        result = await repo.get_inventory("22222222-2222-2222-2222-222222222222")

    assert len(result) == 1
    assert result[0].item_name == "회복 포션"
    assert result[0].scenario_item_id == "item-healing-potion-1"
    assert result[0].item_type == "consumable"
