SELECT *
FROM cypher('state_db_item_logic', $$
  \i used_item.cypher
$$) AS (v agtype);
