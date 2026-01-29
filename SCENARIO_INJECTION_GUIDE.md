# Scenario Injection Guide (Hand-held)

This document provides the Pydantic model structures and JSON examples required to inject a new scenario into the GTRPGM State Manager, including Apache AGE graph relations.

## Endpoint
- **POST** `/state/scenario/inject`

## 1. Data Structure (Pydantic Models)

> **IMPORTANT**: All `id` fields (item_id, scenario_npc_id, scenario_enemy_id, etc.) must be in valid **UUID v4 format**.

```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ScenarioInjectNPC(BaseModel):
    """NPC Template Data"""
    scenario_npc_id: str = Field(..., description="Unique UUID for this NPC template")
    name: str = Field(..., description="NPC Name")
    description: str = Field("", description="Brief biography or role")
    tags: List[str] = Field(default=["npc"], description="Searchable tags")
    state: Dict[str, Any] = Field(
        default={
            "numeric": {"HP": 100, "MP": 50, "SAN": 10},
            "boolean": {}
        },
        description="Initial stats and flags"
    )

class ScenarioInjectEnemy(BaseModel):
    """Enemy Template Data"""
    scenario_enemy_id: str = Field(..., description="Unique UUID for this Enemy template")
    name: str = Field(..., description="Enemy Name")
    description: str = Field("", description="Lore or combat style")
    tags: List[str] = Field(default=["enemy"], description="Category tags")
    state: Dict[str, Any] = Field(
        default={
            "numeric": {"HP": 100, "MP": 0},
            "boolean": {}
        },
        description="Combat stats"
    )
    dropped_items: List[str] = Field(default_factory=list, description="List of Master Item UUIDs")

class ScenarioInjectItem(BaseModel):
    """Item Template Data"""
    item_id: str = Field(..., description="Fixed UUID for the Master Item")
    name: str = Field(..., description="Item Name")
    description: str = Field("", description="Function or flavor text")
    item_type: str = Field("misc", description="consumable, equipment, material, etc.")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Custom properties")

class ScenarioInjectRelation(BaseModel):
    """Relation (Edge) between Entities (Apache AGE)"""
    from_id: str = Field(..., description="scenario_npc_id or scenario_enemy_id (UUID)")
    to_id: str = Field(..., description="scenario_npc_id or scenario_enemy_id (UUID)")
    relation_type: str = Field("neutral", description="friend, foe, rival, etc.")
    affinity: int = Field(50, ge=0, le=100)
    meta: Dict[str, Any] = Field(default_factory=dict)
```

## 2. Complete JSON Example

```json
{
  "title": "The Whispering Caves",
  "description": "A deep dive into the forgotten mines of Moria.",
  "author": "Legendary DM",
  "version": "1.2.0",
  "difficulty": "hard",
  "genre": "dark-fantasy",
  "tags": ["dungeon-crawl", "mystery"],
  "total_acts": 3,
  "items": [
    {
      "item_id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Dim-lit Lantern",
      "description": "A lantern that flickers when spirits are near.",
      "item_type": "equipment",
      "meta": {"range": 10, "fuel": 100}
    }
  ],
  "npcs": [
    {
      "scenario_npc_id": "a1b2c3d4-e5f6-4789-8abc-def123456789",
      "name": "Eldrin the Wise",
      "description": "An old dwarf who knows the cave's secrets.",
      "tags": ["guide", "merchant"],
      "state": {
        "numeric": {"HP": 80, "MP": 200, "SAN": 100},
        "boolean": {"is_immortal": false}
      }
    }
  ],
  "enemies": [
    {
      "scenario_enemy_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "name": "Shadow Stalker",
      "description": "A creature that merges with the cave walls.",
      "tags": ["undead", "stealth"],
      "state": {
        "numeric": {"HP": 120, "MP": 0},
        "boolean": {"can_fly": false}
      },
      "dropped_items": ["550e8400-e29b-41d4-a716-446655440001"]
    }
  ],
  "relations": [
    {
      "from_id": "a1b2c3d4-e5f6-4789-8abc-def123456789",
      "to_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "relation_type": "hostile",
      "affinity": 0,
      "meta": {"reason": "Ancient grudge"}
    }
  ]
}
```

## 3. Important Notes
1. **Strict UUIDs**: Ensure all identifier strings follow the UUID v4 standard (8-4-4-4-12 hex digits).
2. **Session 0**: Data is stored under the master session ID `00000000-0000-0000-0000-000000000000`.
3. **Auto-Cloning**: New sessions will create deep copies using these template UUIDs as reference.
