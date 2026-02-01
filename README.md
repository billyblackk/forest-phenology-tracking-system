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
- Response model for point phenology queries:
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
- The API currently has a mock phenology endpoint in `src/fpts/api/main.py`:

```http
GET /phenology/point?lat=...&lon=...&year=...
```
- validates:
    - `lat` in [-90, 90]
    - `lon` in [-180, 180]
    - `year` in [2000, 2010]
- Logs the request
- Returns a `PhenologyPointResponse` with realistic-looking mock dadtes (fixed pattern based on the year):
```json

{
    "year": 2020,
    "location": {
        "lat": 52.5,
        "lon": 13.4
    },
    "sos_date": "2020-04-15",
    "eos_date": "2020-10-15",
    "season_length": 183,
    "is_forest": true
}
```

Later, the endpoint will be wired to `QueryStorage` + real storage.

### 9. Tech Stack

- Language: Python (3.11+/3.12)
- Environment & Packaging: Poetry
- Web Framework: FastAPI
- ASGI Server: Uvicorn
- Configuration: pydantic-settings
- Data Modeling:
- Python dataclasses for domain models
- Pydantic models for API schemas
- Logging: Standard library logging with centralized setup
- Planned additions:
- Postgres + PostGIS for phenology metrics
- rasterio / rioxarray / xarray for raster data processing
- Background processing pipelines for ingestion and phenology metric computation

### 10. Getting started

Prerequisites
- Python 3.11+ (preferably 3.12).
- Poetry Installed.
- (Optional) Git & GitHub for version control.


#### Install dependencies
From the project root:
```bash
poetry install
```


#### Run the API
The server will start on `http://0.0.0.0:8000`
```bash
poetry run python -m fpts.api
```

Check:
- Health Endpoint:
```bash
curl http://localhost:8000/health
```

- Phenology (mock) endpoint:
```bash
curl "http://localhost:8000/phenology/point?lat=52.5&lon=13.48&year=2020"
```


### 10. Current Project Structure

```text
forest-phenology-tracking-system/
├── pyproject.toml
├── .env                # Local config (not for secrets)
├── src/
│   └── fpts/
│       ├── api/
│       │   ├── __init__.py
│       │   ├── main.py          # FastAPI app + endpoints
│       │   └── schemas.py       # Pydantic API models
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py      # pydantic-settings configuration
│       ├── domain/
│       │   ├── __init__.py
│       │   └── models.py        # Location, PhenologyMetric
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── phenology_repository.py   # Abstract repo interface
│       │   └── in_memory_repository.py   # Simple in-memory implementation
│       ├── query/
│       │   ├── __init__.py
│       │   └── service.py       # QueryService (read-only logic)
│       ├── ingestion/
│       │   └── __init__.py      # (planned)
│       ├── processing/
│       │   └── __init__.py      # (planned)
│       ├── cli/
│       │   └── __init__.py      # (planned CLI commands)
│       └── utils/
│           ├── __init__.py
│           └── logging.py       # Central logging setup
└── tests/                       # (planned)
```

### 11. Roadmap (Planned Work)
The following features are planned but not yet implemented:
1. Raster Ingestion & Processing
- Ingest MODIS phenology/vegetation products
- Use rasterio / rioxarray to:
    - Clip to region of interest
    - Mask forest pixels
    - Derive per-pixel phenology metrics

2. Persistent Storage (PostGIS)
- Store derived PhenologyMetric entries in Postgres/PostGIS
- Add spatial indexes for efficient point & polygon queries
- Implement a PostgresPhenologyRepository that implements PhenologyRepository

3. API Extensions
- `/phenology/timeseries` – per-location multi-year time series
- `/phenology/area` – aggregated metrics for a polygon (e.g. forest reserve)
- Standardized error responses and better error handling

4. Background Jobs & CLI
- CLI commands for:
    - `fpts ingest --year 2020`
    - `fpts process --year 2020`
- Background jobs for heavy workloads

5. Testing & CI
- Unit tests for:
    - domain models
    - repositories
    - API routes
- Integration tests for basic flows
- GitHub Actions workflow for:
    `poetry install`
    `pytest`
    linting/formatting

6. Deployment & Docker
- Dockerfile for the API
- `docker-compose` for API + Postgres
- Production configuration examples


### 12. Contribution / Usage

Right now, this repository is primarily a personal portfolio project showcasing:
- Backend architecture skills
- Proper layering (API → service → repo → domain)
- Clean config and logging setup

Future contributors can extend the system with:
- Real raster ingestion code
- Real database storage
- More sophisticated APIs and metrics.