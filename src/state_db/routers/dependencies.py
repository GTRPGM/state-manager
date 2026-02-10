"""Shared dependency injection helpers for routers."""

from state_db.repositories import (
    EntityRepository,
    LifecycleStateRepository,
    PlayerRepository,
    ProgressRepository,
    ScenarioRepository,
    SessionRepository,
    TraceRepository,
)
from state_db.services import StateService


def get_session_repo() -> SessionRepository:
    return SessionRepository()


def get_progress_repo() -> ProgressRepository:
    return ProgressRepository()


def get_lifecycle_repo() -> LifecycleStateRepository:
    return LifecycleStateRepository()


def get_player_repo() -> PlayerRepository:
    return PlayerRepository()


def get_entity_repo() -> EntityRepository:
    return EntityRepository()


def get_trace_repo() -> TraceRepository:
    return TraceRepository()


def get_scenario_repo() -> ScenarioRepository:
    return ScenarioRepository()


def get_state_service() -> StateService:
    return StateService()
