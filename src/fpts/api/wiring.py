from fpts.config.settings import Settings
from fpts.query.service import QueryService
from fpts.storage.in_memory_repository import InMemoryPhenologyRepository
from fpts.storage.local_raster_repository import LocalRasterRepository


def wire_in_memory_services(app) -> None:
    """
    Temporary wiring for development/testing.
    Later, this will be replaced with PostGIS wiring.
    """

    settings = Settings()

    # Raster repository (local filesystem)
    app.state.raster_repo = LocalRasterRepository(data_dir=settings.data_dir)

    # Phenology repository(in-memory for now)
    repo = InMemoryPhenologyRepository()
    app.state.phenology_repo = repo
    app.state.query_service = QueryService(repository=repo)
