from pathlib import Path

from fpts.storage.raster_repository import RasterRepository


class LocalRasterRepository(RasterRepository):
    """
    Local filesystem implementation.

    Folder convention (v1):
      {data_dir}/raw/{product}/{year}.tif

    Example:
      data/raw/mcd12q2/2020.tif
    """

    def __init__(self, data_dir: str | Path) -> None:
        self._data_dir = Path(data_dir)

    def raw_raster_path(self, product: str, year: int) -> Path:
        return self._data_dir / "raw" / product / f"{year}.tif"

    def exists(self, product: str, year: int) -> bool:
        return self.raw_raster_path(product, year).exists()
