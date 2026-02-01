# Forest Phenology Tracking System (FPTS)

A backend service for exploring forest phenology (seasonal vegetation dynamics) built with production-style software engineering practices.

> **Status:** Early development – core scaffolding, API skeleton, configuration, logging, and basic domain models are in place.

---

## Project Goal

The Forest Phenology Tracking System (FPTS) will ingest satellite-based phenology and vegetation data, derive forest phenology metrics (e.g. start and end of growing season, season length), and expose them via a clean, well-structured API.

The focus is **not** just data analysis, but building a **backend system** with:

- Clear modular architecture
- Proper configuration and logging
- Testable domain logic
- Clean separation between API, services, and storage
- Future-ready for PostGIS and raster processing

---

## What’s Implemented So Far

### 1. Project Structure & Tooling

- Python project managed with **Poetry**
- `src/` layout with a dedicated package:

  ```text
  src/fpts/
    api/
    config/
    domain/
    storage/
    query/
    ingestion/
    processing/
    cli/
    utils/
  ```

pyproject.toml configured so fpts is importable from src/

### 2. Basic FastAPI Application

- FastAPI app defined in `src/fpts/api/main.py`
- ASGI server run via:
```bash
poetry run python -m fpts.api
```

- Health check endpoint:
```http
GET /health
```

- Health check returns basic service info:
```json
{
  "status": "ok",
  "environment": "development",
  "log_level": "info"
}
```

### 3. Configuration System

Configuration is handled using pydantic-settings:
- `src/fpts/config/settings.py` defines a Settings class:
```python
class Settings(BaseSettings):
    app_name: str = "Forest Phenology Tracking System"
    environment: str = "development"
    log_level: str = "info"
```

- Reads values from environment variables and an optional .env file.

- .env example (for local development):
```env
ENVIRONMENT=development
LOG_LEVEL=info
```

-  Settings are instantiated once at app startup and used throughout the app.

### 4. Logging

- Centralized logging utilities in `src/fpts/utils/logging.py`:
- `setup_logging(level: str = "INFO")` configures the root logger:
- - Logs to stdout
- - Format: `timestamp | level | logger_name | message`
- get_logger(name: Optional[str] = None) returns a logger with the global configuration.

- Integrated into the FastAPI app:
```python
settings = Settings()
setup_logging(level=settings.log_level)
logger = get_logger(__name__)
```

- Example log message from `/health` and `/phenology/point`:
```text
2025-12-04 12:34:56 | INFO | fpts.api.main | Health check endpoint called
2025-12-04 12:35:10 | INFO | fpts.api.main | Phenology point query received
```

### 5. Domain Models

- Located in `src/fpts/domain/models.py`.

#### `Location`
- Represents a geographic point:
```python
@dataclass(frozen=True)
class Location:
    lat: float
    lon: float

    def __post_init__(self) -> None:
        if not (-90.0 <= self.lat <= 90.0):
            raise ValueError(...)
        if not (-180.0 <= self.lon <= 180.0):
            raise ValueError(...)
```
- Uses WGS84 lat/lon
- Validates coordinate ranges on construction
- Immutable (`frozen=True`) and hashable

#### `PhenologyMetric`
- Represents phenology metrics at a single location and year:
```python
@dataclass(frozen=True)
class PhenologyMetric:
    year: int
    location: Location
    sos_date: Optional[date]         # Start of season
    eos_date: Optional[date]         # End of season
    season_length: Optional[int]     # Duration in days
    is_forest: bool                  # Whether this pixel is classified as forest
```
- Currently used for interval wiring and as the core domain concept for storage and queries

### 6. API Schemas
- Defined at `src/fpts/api/schemas.py` using Pydantic

#### LocationSchema
- Valdiation and serialisation shape for API traffic
```python
class LocationSchema(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)

    class Config:
        frozen = True
```

#### `PhenologyPointResponse`
- Response model ffor point phenology queries:
```python
class PhenologyPointResponse(BaseModel):
    year: int
    location: LocationSchema
    sos_date: Optional[date] = None
    eos_date: Optional[date] = None
    season_length: Optional[int] = None
    is_forest: bool

    class Config:
        frozen = True
```

### 7. Repository Abstractions & Query Service

#### `PhenologyRepository` (interface)
- Defined in `src/fpts/storage/phenology_repository.py`:
```python
class PhenologyRepository(ABC):
    @abstractmethod
    def get_metric_for_location(
        self,
        location: Location,
        year: int,
    ) -> Optional[PhenologyMetric]:
        ...
```
- This is an abstract contract that future storage implementations (e.g. PostGIS) must satisfy.

#### `InMemoryPhenologyRepository`
- A simple in-memory implementation in `src/fpts/storage/in_memory_repository.py`:
```python
class InMemoryPhenologyRepository(PhenologyRepository):
    def __init__(self) -> None:
        self._store: Dict[Tuple[float, float, int], PhenologyMetric] = {}

    def add_metric(self, metric: PhenologyMetric) -> None:
        key = (metric.location.lat, metric.location.lon, metric.year)
        self._store[key] = metric

    def get_metric_for_location(
        self,
        location: Location,
        year: int,
    ) -> Optional[PhenologyMetric]:
        key = (location.lat, location.lon, year)
        return self._store.get(key)
```
- Used for early wiring and future tests without needing a real database.

#### `QueryService`
- Located at `src/fpts/query/service.py`:
```python
class QueryService:
    def __init__(self, repository: PhenologyRepository) -> None:
        self._repository = repository

    def get_point_metric(
        self,
        location: Location,
        year: int,
    ) -> Optional[PhenologyMetric]:
        return self._repository.get_metric_for_location(location, year)
```
- This is the read-only application service that the API layer will depend on.

###  8. First Phenology Endpoint (Mock)
- 

