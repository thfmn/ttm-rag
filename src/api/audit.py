"""
Audit logging utilities for the Thai Traditional Medicine RAG Bot.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Request
import os

# Set up audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Create audit log file handler if not in production
if os.getenv("ENVIRONMENT", "development") == "development":
    handler = logging.FileHandler("audit.log")
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    audit_logger.addHandler(handler)

class AuditLogger:
    """Audit logger for tracking important events and actions."""
    
    @staticmethod
    def log_event(
        event_type: str,
        user: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log an audit event.
        
        Args:
            event_type (str): Type of event (e.g., "user_login", "data_access")
            user (Optional[str]): Username or user identifier
            ip_address (Optional[str]): IP address of the request
            details (Optional[Dict[str, Any]]): Additional details about the event
        """
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user": user,
            "ip_address": ip_address,
            "details": details or {}
        }
        
        audit_logger.info(json.dumps(audit_data))
    
    @staticmethod
    def log_request(request: Request, user: Optional[str] = None):
        """
        Log an HTTP request.
        
        Args:
            request (Request): FastAPI request object
            user (Optional[str]): Username or user identifier
        """
        # Get client IP address
        ip_address = request.client.host if request.client else None
        
        # Log the request
        AuditLogger.log_event(
            event_type="http_request",
            user=user,
            ip_address=ip_address,
            details={
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "query_params": dict(request.query_params)
            }
        )
    
    @staticmethod
    def log_data_access(
        data_type: str,
        action: str,
        user: Optional[str] = None,
        ip_address: Optional[str] = None,
        record_count: Optional[int] = None
    ):
        """
        Log data access events.
        
        Args:
            data_type (str): Type of data accessed (e.g., "pubmed_articles")
            action (str): Action performed (e.g., "search", "retrieve")
            user (Optional[str]): Username or user identifier
            ip_address (Optional[str]): IP address of the request
            record_count (Optional[int]): Number of records accessed
        """
        AuditLogger.log_event(
            event_type="data_access",
            user=user,
            ip_address=ip_address,
            details={
                "data_type": data_type,
                "action": action,
                "record_count": record_count
            }
        )
    
    @staticmethod
    def log_security_event(
        event_type: str,
        description: str,
        user: Optional[str] = None,
        ip_address: Optional[str] = None,
        severity: str = "medium"
    ):
        """
        Log security-related events.
        
        Args:
            event_type (str): Type of security event (e.g., "failed_login", "unauthorized_access")
            description (str): Description of the event
            user (Optional[str]): Username or user identifier
            ip_address (Optional[str]): IP address of the request
            severity (str): Severity level ("low", "medium", "high", "critical")
        """
        AuditLogger.log_event(
            event_type=f"security_{event_type}",
            user=user,
            ip_address=ip_address,
            details={
                "description": description,
                "severity": severity
            }
        )