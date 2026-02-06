MATCH (s:Session {id: $session_id})
CREATE (n:NPC {
    npc_id: $npc_id,
    session_id: $session_id,
    scenario_id: s.scenario_id,
    scenario_npc_id: $scenario_npc_id,
    name: $name,
    description: $description,
    state: $state,
    tags: $tags,
    is_departed: false,
    active: true
})
CREATE (s)-[:HAS_ENTITY]->(n)
RETURN {id: n.npc_id, name: n.name}
