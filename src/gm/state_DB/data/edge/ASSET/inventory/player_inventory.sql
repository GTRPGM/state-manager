SELECT *
FROM cypher('state_db_item_logic', $$
  \i player_inventory.cypher
$$) AS (v agtype);
