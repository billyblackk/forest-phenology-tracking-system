from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin


def write_small_geotiff(path: Path, value: float) -> None:
    """
    Tiny 32x32 single-band float32 GeoTIFF in EPSG:4326.

    Deterministic + small => safe to commit for offline tests.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    data = np.full((32, 32), value, dtype=np.float32)

    # arbitrary but valid georeferencing
    transform = from_origin(west=-0.5, north=51.5, xsize=0.01, ysize=0.01)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
        nodata=-9999.0,
    ) as dst:
        dst.write(data, 1)


def main() -> None:
    base = Path("tests/fixtures/raw/mod13q1/2020")
    write_small_geotiff(base / "doy_001.tif", 0.10)
    write_small_geotiff(base / "doy_017.tif", 0.20)
    write_small_geotiff(base / "doy_033.tif", 0.30)
    print(f"Wrote fixture files under {base}")


if __name__ == "__main__":
    main()
