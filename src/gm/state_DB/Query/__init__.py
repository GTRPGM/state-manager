# src/gm/state_DB/Query/__init__.py
# Query 모듈 초기화

from .query import (
    # 앱 생명주기
    shutdown,
    startup,
    # 세션 관리
    session_start,
    session_end,
    session_pause,
    session_resume,
    get_active_sessions,
    get_session_info,
    # 조회
    get_session_inventory,
    get_session_npcs,
    get_session_enemies,
    get_player_stats,
    get_player_state,
    get_npc_relations,
    get_item_info,
    # 업데이트
    update_player_hp,
    update_player_stats,
    update_npc_affinity,
    update_enemy_hp,
    defeat_enemy,
    update_location,
    inventory_update,
    # 관리
    spawn_enemy,
    remove_enemy,
    spawn_npc,
    remove_npc,
    # Phase/Turn/Act
    change_phase,
    get_current_phase,
    add_turn,
    get_current_turn,
    change_act,
    change_sequence,
    # 그래프
    get_graph_nodes,
    get_graph_edges,
    get_subgraph,
)

__all__ = [
    # 앱 생명주기
    "startup",
    "shutdown",
    # 세션 관리
    "session_start",
    "session_end",
    "session_pause",
    "session_resume",
    "get_active_sessions",
    "get_session_info",
    # 조회
    "get_session_inventory",
    "get_session_npcs",
    "get_session_enemies",
    "get_player_stats",
    "get_player_state",
    "get_npc_relations",
    "get_item_info",
    # 업데이트
    "update_player_hp",
    "update_player_stats",
    "update_npc_affinity",
    "update_enemy_hp",
    "defeat_enemy",
    "update_location",
    "inventory_update",
    # 관리
    "spawn_enemy",
    "remove_enemy",
    "spawn_npc",
    "remove_npc",
    # Phase/Turn/Act
    "change_phase",
    "get_current_phase",
    "add_turn",
    "get_current_turn",
    "change_act",
    "change_sequence",
    # 그래프
    "get_graph_nodes",
    "get_graph_edges",
    "get_subgraph",
]