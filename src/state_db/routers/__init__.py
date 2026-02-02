"""Router modules for state management API.

This package contains separated routers organized by Query folder structure:
- router_START: Session initialization (Query/START_by_session)
- router_INQUIRY: Data retrieval and queries (Query/INQUIRY)
- router_UPDATE: State modifications (Query/UPDATE)
- router_MANAGE: Entity and session management (Query/MANAGE)
- router_TRACE: History tracking and analysis (Query/TRACE)
- router_PROXY: Microservice proxy health check
"""

from . import (
    router_INJECT,
    router_INQUIRY,
    router_MANAGE,
    router_PROXY,
    router_START,
    router_TRACE,
    router_TRACE_phase,
    router_UPDATE,
)

__all__ = [
    "router_INJECT",
    "router_START",
    "router_INQUIRY",
    "router_UPDATE",
    "router_MANAGE",
    "router_TRACE",
    "router_TRACE_phase",
    "router_PROXY",
]
