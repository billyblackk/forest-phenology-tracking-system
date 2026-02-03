from abc import ABC, abstractmethod
from pathlib import Path


class RasterRepository(ABC):
    """
    Abstract interface for finding and managing raw raster files.
    """

    @abstractmethod
    def raw_raster_path(self, product: str, year: int) -> Path:
        """
        Return the expected path for a raw raster for (product, year).
        Does not guarantee the file exists.
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self, product: str, year: int) -> bool:
        """
        Return True if the raster file exists locally.
        """
        raise NotImplementedError
