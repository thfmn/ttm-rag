"""
Custom exceptions for the Thai Traditional Medicine RAG Bot.

This module defines custom exception classes for different types of errors
that can occur in the application, providing more specific error handling
and better error messages.
"""

from typing import Optional, Any
import requests


class PubMedError(Exception):
    """Base exception class for PubMed-related errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
        url: Optional[str] = None,
        context: Optional[dict] = None
    ):
        """
        Initialize the PubMedError.
        
        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_text: Response text if applicable
            url: URL that caused the error if applicable
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        self.url = url
        self.context = context or {}


class PubMedAPIError(PubMedError):
    """Exception for PubMed API errors."""
    pass


class PubMedParseError(PubMedError):
    """Exception for PubMed XML parsing errors."""
    pass


class PubMedRateLimitError(PubMedError):
    """Exception for PubMed rate limiting errors."""
    pass


class PubMedNotFoundError(PubMedError):
    """Exception for PubMed not found errors (404)."""
    pass


class PubMedValidationError(PubMedError):
    """Exception for PubMed data validation errors."""
    pass


class PubMedNetworkError(PubMedError):
    """Exception for network-related errors."""
    
    def __init__(
        self, 
        message: str, 
        original_exception: Optional[Exception] = None,
        context: Optional[dict] = None
    ):
        """
        Initialize the PubMedNetworkError.
        
        Args:
            message: Error message
            original_exception: The original exception that caused this error
            context: Additional context information
        """
        super().__init__(message, context=context)
        self.original_exception = original_exception


def create_pubmed_error_from_response(response: requests.Response, context: Optional[dict] = None) -> PubMedError:
    """
    Create an appropriate PubMedError from an HTTP response.
    
    Args:
        response: HTTP response object
        context: Additional context information
        
    Returns:
        Appropriate PubMedError subclass
    """
    context = context or {}
    context.update({
        'status_code': response.status_code,
        'url': response.url
    })
    
    # Handle specific status codes
    if response.status_code == 404:
        return PubMedNotFoundError(
            f"Resource not found: {response.url}",
            status_code=response.status_code,
            response_text=response.text,
            url=response.url,
            context=context
        )
    elif response.status_code == 429:
        return PubMedRateLimitError(
            f"Rate limit exceeded for {response.url}",
            status_code=response.status_code,
            response_text=response.text,
            url=response.url,
            context=context
        )
    elif 400 <= response.status_code < 500:
        return PubMedAPIError(
            f"Client error {response.status_code}: {response.url}",
            status_code=response.status_code,
            response_text=response.text,
            url=response.url,
            context=context
        )
    elif 500 <= response.status_code < 600:
        return PubMedAPIError(
            f"Server error {response.status_code}: {response.url}",
            status_code=response.status_code,
            response_text=response.text,
            url=response.url,
            context=context
        )
    else:
        return PubMedAPIError(
            f"HTTP error {response.status_code}: {response.url}",
            status_code=response.status_code,
            response_text=response.text,
            url=response.url,
            context=context
        )