"""
Unit tests for custom exception classes.

These tests verify that our custom exception classes work correctly
and provide the expected functionality.
"""

import sys
import os
import pytest
import requests

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.exceptions import (
    PubMedError,
    PubMedAPIError,
    PubMedParseError,
    PubMedRateLimitError,
    PubMedNotFoundError,
    PubMedValidationError,
    PubMedNetworkError,
    create_pubmed_error_from_response
)


class TestPubMedError:
    """Tests for the base PubMedError class."""
    
    def test_pubmed_error_creation(self):
        """Test creating a basic PubMedError."""
        error = PubMedError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.status_code is None
        assert error.response_text is None
        assert error.url is None
        assert error.context == {}
    
    def test_pubmed_error_with_details(self):
        """Test creating a PubMedError with additional details."""
        context = {"query": "test query", "max_results": 10}
        error = PubMedError(
            "Test error message",
            status_code=400,
            response_text="Bad Request",
            url="https://example.com",
            context=context
        )
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.status_code == 400
        assert error.response_text == "Bad Request"
        assert error.url == "https://example.com"
        assert error.context == context


class TestSpecificExceptions:
    """Tests for specific PubMed exception classes."""
    
    def test_pubmed_api_error(self):
        """Test PubMedAPIError."""
        error = PubMedAPIError("API error")
        assert isinstance(error, PubMedError)
        assert str(error) == "API error"
    
    def test_pubmed_parse_error(self):
        """Test PubMedParseError."""
        error = PubMedParseError("Parse error")
        assert isinstance(error, PubMedError)
        assert str(error) == "Parse error"
    
    def test_pubmed_rate_limit_error(self):
        """Test PubMedRateLimitError."""
        error = PubMedRateLimitError("Rate limit error")
        assert isinstance(error, PubMedError)
        assert str(error) == "Rate limit error"
    
    def test_pubmed_not_found_error(self):
        """Test PubMedNotFoundError."""
        error = PubMedNotFoundError("Not found error")
        assert isinstance(error, PubMedError)
        assert str(error) == "Not found error"
    
    def test_pubmed_validation_error(self):
        """Test PubMedValidationError."""
        error = PubMedValidationError("Validation error")
        assert isinstance(error, PubMedError)
        assert str(error) == "Validation error"
    
    def test_pubmed_network_error(self):
        """Test PubMedNetworkError."""
        original_exception = Exception("Network error")
        error = PubMedNetworkError("Network error", original_exception=original_exception)
        assert isinstance(error, PubMedError)
        assert str(error) == "Network error"
        assert error.original_exception == original_exception


class TestCreatePubMedErrorFromResponse:
    """Tests for the create_pubmed_error_from_response function."""
    
    def test_404_error(self):
        """Test creating a PubMedNotFoundError from a 404 response."""
        response = requests.Response()
        response.status_code = 404
        response._content = b"Not Found"
        response.url = "https://example.com"
        
        error = create_pubmed_error_from_response(response)
        assert isinstance(error, PubMedNotFoundError)
        assert error.status_code == 404
        assert error.url == "https://example.com"
    
    def test_429_error(self):
        """Test creating a PubMedRateLimitError from a 429 response."""
        response = requests.Response()
        response.status_code = 429
        response._content = b"Rate Limit Exceeded"
        response.url = "https://example.com"
        
        error = create_pubmed_error_from_response(response)
        assert isinstance(error, PubMedRateLimitError)
        assert error.status_code == 429
        assert error.url == "https://example.com"
    
    def test_400_error(self):
        """Test creating a PubMedAPIError from a 400 response."""
        response = requests.Response()
        response.status_code = 400
        response._content = b"Bad Request"
        response.url = "https://example.com"
        
        error = create_pubmed_error_from_response(response)
        assert isinstance(error, PubMedAPIError)
        assert error.status_code == 400
        assert error.url == "https://example.com"
    
    def test_500_error(self):
        """Test creating a PubMedAPIError from a 500 response."""
        response = requests.Response()
        response.status_code = 500
        response._content = b"Internal Server Error"
        response.url = "https://example.com"
        
        error = create_pubmed_error_from_response(response)
        assert isinstance(error, PubMedAPIError)
        assert error.status_code == 500
        assert error.url == "https://example.com"
    
    def test_other_error(self):
        """Test creating a PubMedAPIError from an unexpected status code."""
        response = requests.Response()
        response.status_code = 300
        response._content = b"Multiple Choices"
        response.url = "https://example.com"
        
        error = create_pubmed_error_from_response(response)
        assert isinstance(error, PubMedAPIError)
        assert error.status_code == 300
        assert error.url == "https://example.com"