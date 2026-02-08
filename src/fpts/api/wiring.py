from fpts.config.settings import Settings

from fpts.query.service import QueryService
from fpts.processing.raster_service import RasterService
from fpts.processing.phenology_service import PhenologyComputationService

from fpts.storage.local_raster_repository import LocalRasterRepository
from fpts.storage.in_memory_repository import InMemoryPhenologyRepository


def wire_in_memory_services(app, settings: Settings) -> None:
    """
    Temporary wiring for development/testing.

    We pass Settings in explicitly so tests can override config cleanly.
    """
    # Local raster repo to read from.
    app.state.raster_repo = LocalRasterRepository(data_dir=settings.data_dir)
    app.state.raster_service = RasterService(raster_repo=app.state.raster_repo)
    app.state.phenology_compute_service = PhenologyComputationService(
        raster_repo=app.state.raster_repo
    )

    # In memory phenology repo to store and read metrics.
    repo = InMemoryPhenologyRepository()
    app.state.phenology_repo = repo
    app.state.query_service = QueryService(repository=repo)
