from typing import Optional

from fpts.cache.keys import point_metric_cache_key
from fpts.cache.ttl_cache import InMemoryTTLCache
from fpts.domain.models import Location, PhenologyMetric
from fpts.storage.phenology_repository import PhenologyRepository


class QueryService:
    """
    Application service for read-only phenology queries.

    The API layer will depend on this service instead of talking
    to repositories or storage directly.

    Returns metrics for a point (lat, long, year)
    """

    def __init__(
        self,
        repository: PhenologyRepository,
        point_cache: InMemoryTTLCache[str, PhenologyMetric] | None = None,
    ) -> None:
        self._repository = repository
        self._point_cache = point_cache

    def get_point_metric(
        self, product: str, location: Location, year: int
    ) -> Optional[PhenologyMetric]:
        """
        Return phenology metric for a single location and year, or None if not found
        """
        if self._point_cache is not None:
            key = point_metric_cache_key(
                source="repo",
                product=product,
                year=year,
                location=location,
                threshold_frac=None,
            )
            cached = self._point_cache.get(key)
            if cached is not None:
                return cached

        metric = self._repository.get_metric_for_location(
            product=product, location=location, year=year
        )

        if metric is not None and self._point_cache is not None:
            self._point_cache.set(key, metric)

        return metric

    def get_point_timeseries(
        self,
        *,
        product: str,
        location: Location,
        start_year: int,
        end_year: int,
    ) -> list[PhenologyMetric]:
        return self._repository.get_timeseries_for_location(
            product=product,
            location=location,
            start_year=start_year,
            end_year=end_year,
        )

    def get_area_stats(
        self,
        *,
        product: str,
        year: int,
        polygon_geojson: dict,
        only_forest: bool = False,
        min_season_length: int | None = None,
        season_length_stat: str = "mean",
    ) -> dict | None:
        return self._repository.get_area_stats(
            product=product,
            year=year,
            polygon_geojson=polygon_geojson,
            only_forest=only_forest,
            min_season_length=min_season_length,
            season_length_stat=season_length_stat,
        )
