SELECT *
FROM cypher('trpg_graph', $$
  \i edge/cypher/player_inventory.cypher
$$) AS (v agtype);