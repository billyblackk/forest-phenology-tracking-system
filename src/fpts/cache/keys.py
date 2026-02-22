from __future__ import annotations

from fpts.domain.models import Location


def point_metric_cache_key(
    *,
    source: str,  # "repo" or "compute"
    product: str,
    year: int,
    location: Location,
    threshold_frac: float | None,
) -> str:
    """
    Normalize floats so equivalent requests map to the same key.

    - lat/lon rounded to 6dp: ~0.11m precision at equator (more than enough here)
    - threshold rounded to 3dp
    """
    lat = round(location.lat, 6)
    lon = round(location.lon, 6)
    thr = None if threshold_frac is None else round(threshold_frac, 3)
    return f"phenology:point:{source}:{product}:{year}:{lat}:{lon}:{thr}"
