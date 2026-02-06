from fpts.config.settings import Settings
from fpts.query.service import QueryService
from fpts.storage.in_memory_repository import InMemoryPhenologyRepository
from fpts.storage.local_raster_repository import LocalRasterRepository
from fpts.processing.raster_service import RasterService
from fpts.processing.phenology_service import PhenologyComputationService


def wire_in_memory_services(app, settings: Settings) -> None:
    """
    Temporary wiring for development/testing.

    We pass Settings in explicitly so tests can override config cleanly.
    """
    app.state.raster_repo = LocalRasterRepository(data_dir=settings.data_dir)
    app.state.raster_service = RasterService(raster_repo=app.state.raster_repo)

    repo = InMemoryPhenologyRepository()
    app.state.phenology_repo = repo
    app.state.query_service = QueryService(repository=repo)

    app.state.phenology_compute_service = PhenologyComputationService(
        raster_repo=app.state.raster_repo
    )
