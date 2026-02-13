import pytest

from fpts.config.settings import Settings
from fpts.api.main import create_app


@pytest.fixture
def app_memory():
    return create_app(
        settings=Settings(
            phenology_repo_backend="memory",
        )
    )
