"""
Test module for the dashboard functionality.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_dashboard_home():
    """Test that the dashboard home page loads correctly."""
    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Thai Traditional Medicine RAG Bot Dashboard" in response.text

def test_dashboard_metrics_api():
    """Test that the dashboard metrics API endpoint works."""
    response = client.get("/dashboard/api/metrics")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    
    data = response.json()
    assert "system_status" in data
    assert "total_documents" in data
    assert "active_sources" in data
    assert "processing_rate" in data
    assert "queue_depth" in data
    assert "sources" in data

def test_dashboard_activity_api():
    """Test that the dashboard activity API endpoint works."""
    response = client.get("/dashboard/api/activity")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    
    data = response.json()
    assert "activities" in data
    assert isinstance(data["activities"], list)

if __name__ == "__main__":
    pytest.main([__file__])