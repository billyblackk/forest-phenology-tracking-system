from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    """
    A Geographic location in WGS84 (Latitude/ Longitude) coordinates.
    """

    lat: float
    lon: float

    def __post_init__(self) -> None:
        if not (-90.0 <= self.lat <= 90.0):
            raise ValueError(f"Latitude must be between -90 and 90, got {self.lat}")
        if not (-180.0 <= self.lon <= 180.0):
            raise ValueError(f"Longitude bust be between -180 and 180, got {self.lon}")
