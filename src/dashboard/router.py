"""
Dashboard router for the Thai Traditional Medicine RAG Bot.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

# Create router
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Set up templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """
    Serve the dashboard home page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/api/metrics")
async def get_dashboard_metrics():
    """
    Get dashboard metrics for real-time updates.
    """
    # This would normally fetch real data from the database or metrics collectors
    return {
        "system_status": "healthy",
        "total_documents": 12500,
        "active_sources": 8,
        "processing_rate": 42.5,
        "queue_depth": 15,
        "sources": {
            "pubmed": 7500,
            "pmc_oa": 3200,
            "dtam": 1800
        }
    }

@router.get("/api/activity")
async def get_recent_activity():
    """
    Get recent activity for the dashboard.
    """
    # This would normally fetch real data from logs or activity tables
    return {
        "activities": [
            {
                "time": "2023-01-01T10:30:00Z",
                "activity": "Document processed from PubMed",
                "details": "Document ID: 12345678",
                "status": "success"
            },
            {
                "time": "2023-01-01T10:25:00Z",
                "activity": "New source connected",
                "details": "PMC Open Access",
                "status": "info"
            },
            {
                "time": "2023-01-01T10:20:00Z",
                "activity": "Validation completed",
                "details": "Batch of 100 documents",
                "status": "success"
            }
        ]
    }