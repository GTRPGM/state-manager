"""Shared dependency injection helpers for routers."""

from state_db.repositories import EntityRepository, PlayerRepository, SessionRepository
from state_db.services import StateService


def get_session_repo() -> SessionRepository:
    return SessionRepository()


def get_player_repo() -> PlayerRepository:
    return PlayerRepository()


def get_entity_repo() -> EntityRepository:
    return EntityRepository()


def get_state_service() -> StateService:
    return StateService()
