"""Router modules for state management API.

This package contains separated routers organized by domain:
- router_SESSION: Session lifecycle and progress management
- router_INQUIRY: Data retrieval and queries
- router_UPDATE: State modifications
- router_MANAGE: Entity management
- router_TRACE: History tracking and analysis
- router_PROXY: Microservice proxy health check
"""

from . import (
    router_COMMIT,
    router_INQUIRY,
    router_MANAGE,
    router_PROXY,
    router_SCENARIO,
    router_SESSION,
    router_TRACE,
    router_UPDATE,
)

__all__ = [
    "router_COMMIT",
    "router_INQUIRY",
    "router_MANAGE",
    "router_PROXY",
    "router_SCENARIO",
    "router_SESSION",
    "router_TRACE",
    "router_UPDATE",
]
