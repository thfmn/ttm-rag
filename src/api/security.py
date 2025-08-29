"""
Security middleware for the Thai Traditional Medicine RAG Bot API.
"""

from fastapi import Request, Response, HTTPException
from fastapi.responses import RedirectResponse
import os

class HTTPSMiddleware:
    """Middleware to enforce HTTPS in production."""
    
    def __init__(self, app):
        self.app = app
        # Check if we're in production environment
        self.is_production = os.getenv("ENVIRONMENT", "development") == "production"
        self.is_https_enabled = os.getenv("HTTPS_ENABLED", "false").lower() == "true"
    
    async def __call__(self, scope, receive, send):
        """Process incoming requests and enforce HTTPS if needed."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope, receive)
        
        # Check if HTTPS enforcement is enabled
        if self.is_production and self.is_https_enabled:
            # Check if the request is using HTTP
            if request.headers.get("x-forwarded-proto", "http") == "http":
                # Redirect to HTTPS
                https_url = request.url.replace(scheme="https")
                response = RedirectResponse(url=https_url, status_code=301)
                await response(scope, receive, send)
                return
                
        # Continue with the request
        await self.app(scope, receive, send)