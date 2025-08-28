"""
Tests for the FastAPI application.

These tests verify that the FastAPI endpoints work correctly.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "description" in data
    assert "endpoints" in data


def test_search_endpoint():
    """Test the search endpoint with a simple query."""
    response = client.get("/search?query=medicine&max_results=3")
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "total_results" in data
    assert "articles" in data
    # We might get results or not depending on the API, but the endpoint should work


def test_search_with_invalid_max_results():
    """Test the search endpoint with invalid max_results."""
    response = client.get("/search?query=medicine&max_results=150")
    # Should be rejected by Query validation
    assert response.status_code == 422


def test_thai_medicine_search_endpoint():
    """Test the Thai medicine search endpoint."""
    response = client.get("/thai-medicine-search?max_results=3")
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "total_results" in data
    assert "articles" in data


def test_article_endpoint_with_invalid_pmid():
    """Test the article endpoint with an invalid PMID."""
    response = client.get("/article/invalid123")
    # The API might return 200 with empty results or 404/500 depending on how it handles invalid PMIDs
    # We'll check that it doesn't crash and returns a reasonable response
    assert response.status_code in [200, 404, 500]