import pytest
from pathlib import Path

@pytest.fixture
def base_dir():
    return Path(__file__).parent.parent
