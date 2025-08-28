"""
Unit tests for retry utilities.

These tests verify that our retry mechanisms work correctly
and handle different types of errors appropriately.
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.retry import (
    RetryConfig,
    retry,
    should_retry_pubmed_error
)
from src.utils.exceptions import (
    PubMedAPIError,
    PubMedNetworkError,
    PubMedRateLimitError,
    PubMedNotFoundError
)


class TestRetryConfig:
    """Tests for the RetryConfig class."""
    
    def test_default_configuration(self):
        """Test creating a RetryConfig with default values."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.backoff_multiplier == 2.0
        assert config.jitter is True
    
    def test_custom_configuration(self):
        """Test creating a RetryConfig with custom values."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=2.0,
            max_delay=30.0,
            backoff_multiplier=1.5,
            jitter=False
        )
        assert config.max_attempts == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 30.0
        assert config.backoff_multiplier == 1.5
        assert config.jitter is False


class TestRetryDecorator:
    """Tests for the retry decorator."""
    
    def test_retry_success_on_first_attempt(self):
        """Test that a function that succeeds on the first attempt is not retried."""
        call_count = 0
        
        @retry()
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        assert result == "success"
        assert call_count == 1
    
    def test_retry_success_on_second_attempt(self):
        """Test that a function that succeeds on the second attempt is retried once."""
        call_count = 0
        
        @retry(exceptions=(Exception,))
        def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First attempt failed")
            return "success"
        
        result = eventually_successful_function()
        assert result == "success"
        assert call_count == 2
    
    def test_retry_max_attempts_reached(self):
        """Test that a function that always fails raises the last exception."""
        call_count = 0
        
        @retry(exceptions=(Exception,), config=RetryConfig(max_attempts=3))
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception(f"Attempt {call_count} failed")
        
        with pytest.raises(Exception, match="Attempt 3 failed"):
            always_failing_function()
        
        assert call_count == 3
    
    def test_retry_wrong_exception_type(self):
        """Test that exceptions not in the retry list are not retried."""
        call_count = 0
        
        @retry(exceptions=(ValueError,))
        def function_raising_wrong_exception():
            nonlocal call_count
            call_count += 1
            raise TypeError("This should not be retried")
        
        with pytest.raises(TypeError, match="This should not be retried"):
            function_raising_wrong_exception()
        
        assert call_count == 1
    
    def test_retry_with_custom_should_retry(self):
        """Test retry with a custom should_retry function."""
        call_count = 0
        
        def custom_should_retry(exception):
            return "should retry" in str(exception)
        
        @retry(
            exceptions=(Exception,),
            config=RetryConfig(max_attempts=3),
            should_retry=custom_should_retry
        )
        def function_with_custom_retry_logic():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("This should retry")
            elif call_count == 2:
                raise Exception("This should not retry")
            return "success"
        
        with pytest.raises(Exception, match="This should not retry"):
            function_with_custom_retry_logic()
        
        assert call_count == 2
        
        assert call_count == 2


class TestShouldRetryPubMedError:
    """Tests for the should_retry_pubmed_error function."""
    
    def test_retry_network_error(self):
        """Test that network errors should be retried."""
        error = PubMedNetworkError("Network error")
        assert should_retry_pubmed_error(error) is True
    
    def test_retry_rate_limit_error(self):
        """Test that rate limit errors should be retried."""
        error = PubMedRateLimitError("Rate limit error")
        assert should_retry_pubmed_error(error) is True
    
    def test_retry_server_error(self):
        """Test that server errors (5xx) should be retried."""
        error = PubMedAPIError("Server error", status_code=500)
        assert should_retry_pubmed_error(error) is True
    
    def test_retry_rate_limit_status_code(self):
        """Test that 429 status codes should be retried."""
        error = PubMedAPIError("Rate limit", status_code=429)
        assert should_retry_pubmed_error(error) is True
    
    def test_no_retry_not_found_error(self):
        """Test that not found errors (404) should not be retried."""
        error = PubMedNotFoundError("Not found")
        assert should_retry_pubmed_error(error) is False
    
    def test_no_retry_client_error(self):
        """Test that client errors (4xx, except 429) should not be retried."""
        error = PubMedAPIError("Client error", status_code=400)
        assert should_retry_pubmed_error(error) is False
    
    def test_no_retry_validation_error(self):
        """Test that validation errors should not be retried."""
        error = ValueError("Validation error")
        assert should_retry_pubmed_error(error) is False