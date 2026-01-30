"""
[DEPRECATED] This module is deprecated and will be removed in future versions.
Please use:
- state_db.infrastructure.connection for DatabaseManager
- state_db.infrastructure.query_executor for query execution
- state_db.infrastructure.lifecycle for startup/shutdown
"""

from state_db.infrastructure.connection import DatabaseManager, set_age_path
from state_db.infrastructure.lifecycle import (
    init_age_graph,
    shutdown,
    startup,
)
from state_db.infrastructure.query_executor import (
    SQL_CACHE,
    execute_sql_function,
    load_queries,
    run_cypher_query,
    run_raw_command,
    run_raw_query,
    run_sql_command,
    run_sql_query,
)

__all__ = [
    "DatabaseManager",
    "set_age_path",
    "init_age_graph",
    "load_queries",
    "run_sql_query",
    "run_raw_query",
    "run_sql_command",
    "run_raw_command",
    "execute_sql_function",
    "run_cypher_query",
    "startup",
    "shutdown",
    "SQL_CACHE",
]
