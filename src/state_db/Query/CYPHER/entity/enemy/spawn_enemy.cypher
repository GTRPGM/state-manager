MATCH (s:Session {id: $session_id})
CREATE (e:Enemy {
    enemy_id: $enemy_id,
    session_id: $session_id,
    scenario_id: s.scenario_id,
    scenario_enemy_id: $scenario_enemy_id,
    name: $name,
    description: $description,
    hp: $hp,
    attack: $attack,
    defense: $defense,
    state: $state,
    tags: $tags,
    is_defeated: false,
    active: true
})
CREATE (s)-[:HAS_ENTITY]->(e)
RETURN {id: e.enemy_id, name: e.name}
