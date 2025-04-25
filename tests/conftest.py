# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from main import app  # путь может отличаться, проверь

@pytest.fixture
def client():
    return TestClient(app)
