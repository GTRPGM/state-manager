SELECT *
FROM cypher('state_db_item_logic', $$
  \i earn_item.cypher
$$) AS (v agtype);
