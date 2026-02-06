from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Literal

from fpts.api.schemas import LocationSchema, PhenologyPointResponse
from fpts.api.dependencies import get_query_service, get_phenology_compute_service
from fpts.domain.models import Location, PhenologyMetric
from fpts.query.service import QueryService
from fpts.utils.logging import get_logger
from fpts.processing.phenology_service import PhenologyComputationService

logger = get_logger(__name__)

router = APIRouter(prefix="/phenology", tags=["phenology"])


@router.get("/point", response_model=PhenologyPointResponse)
def get_point_phenology(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
    year: int = Query(..., ge=2000, le=2100),
    mode: Literal["repo", "compute"] = Query("repo"),
    product: str = Query("ndvi_synth", min_length=1),
    threshold_frac: float = Query(0.5, gt=0.0, lt=1.0),
    query_service: QueryService = Depends(get_query_service),
    compute_service: PhenologyComputationService = Depends(
        get_phenology_compute_service
    ),
):
    """
    Get phenology metrics for a single point.

    mode=repo:
      Reads from repository (currently in-memory; later PostGIS).

    mode=compute:
      Computes from NDVI raster stack on the fly (currently synthetic NDVI stack).
    """
    logger.info(
        f"Phenology point query received: lat: {lat}, lon: {lon}, year: {year}, mode: {mode}, product: {product}, threshold_frac: {threshold_frac}"
    )

    location = Location(lat=lat, lon=lon)

    if mode == "repo":
        metric = query_service.get_point_metric(location=location, year=year)
        if metric is None:
            raise HTTPException(
                status_code=404, detail="No phenology data found for this location/year"
            )
    else:
        # mode == "compute"
        try:
            metric = compute_service.compute_point_phenology(
                product=product,
                year=year,
                location=location,
                threshold_frac=threshold_frac,
            )
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    return PhenologyPointResponse(
        year=metric.year,
        location=LocationSchema(lat=metric.location.lat, lon=metric.location.lon),
        sos_date=metric.sos_date,
        eos_date=metric.eos_date,
        season_length=metric.season_length,
        is_forest=metric.is_forest,
    )
