"""
Monitoring and metrics utilities for the Thai Traditional Medicine RAG Bot.
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Set up logging
logger = logging.getLogger(__name__)

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Number of active HTTP requests'
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring HTTP requests."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process incoming requests and collect metrics."""
        # Increment active requests
        ACTIVE_REQUESTS.inc()
        
        # Record start time
        start_time = time.time()
        
        method = request.method
        endpoint = request.url.path
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Record duration
            duration = time.time() - start_time
            
            # Update metrics
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Record error
            ERROR_COUNT.labels(
                method=method,
                endpoint=endpoint,
                error_type=type(e).__name__
            ).inc()
            
            # Re-raise the exception
            raise
            
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.dec()

# Metrics endpoint handler
async def metrics_endpoint() -> PlainTextResponse:
    """Return Prometheus metrics."""
    try:
        metrics_data = generate_latest()
        return PlainTextResponse(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return PlainTextResponse(
            content="# Error generating metrics",
            status_code=500
        )

# Custom exception handlers for monitoring
def record_error(error_type: str, method: str = "UNKNOWN", endpoint: str = "UNKNOWN"):
    """Record an error in the metrics."""
    ERROR_COUNT.labels(
        method=method,
        endpoint=endpoint,
        error_type=error_type
    ).inc()

def record_rate_limit_error(method: str = "UNKNOWN", endpoint: str = "UNKNOWN"):
    """Record a rate limit error."""
    record_error("RateLimitError", method, endpoint)

def record_pubmed_api_error(method: str = "UNKNOWN", endpoint: str = "UNKNOWN"):
    """Record a PubMed API error."""
    record_error("PubMedAPIError", method, endpoint)