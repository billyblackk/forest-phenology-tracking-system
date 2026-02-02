from fpts.query.service import QueryService
from fpts.storage.in_memory_repository import InMemoryPhenologyRepository


def wire_in_memory_services(app) -> None:
    """
    Temporary wiring for development/testing.
    Later, this will be replaced with PostGIS wiring.
    """
    repo = InMemoryPhenologyRepository()
    app.state.phenology_repo = repo
    app.state.query_service = QueryService(repository=repo)
