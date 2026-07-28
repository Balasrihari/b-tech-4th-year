import pytest
import requests


def test_api_integration():
    """Test that the API is accessible"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    except requests.exceptions.ConnectionError:
        pytest.skip("API server not running")
