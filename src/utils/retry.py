"""
Retry utilities for the Thai Traditional Medicine RAG Bot.

This module provides utilities for implementing retry mechanisms with
exponential backoff for handling transient failures.
"""

import time
import random
import logging
from typing import Callable, Type, Tuple, Set, Optional
from functools import wraps

from src.utils.exceptions import PubMedRateLimitError, PubMedNetworkError

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize the retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            max_delay: Maximum delay between retries in seconds
            backoff_multiplier: Multiplier for exponential backoff
            jitter: Whether to add random jitter to delays
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter


def retry(
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    config: RetryConfig = None,
    should_retry: Optional[Callable[[Exception], bool]] = None
):
    """
    Decorator for retrying function calls with exponential backoff.
    
    Args:
        exceptions: Tuple of exception types to retry on
        config: Retry configuration
        should_retry: Optional function to determine if an exception should be retried
        
    Returns:
        Decorated function
    """
    if config is None:
        config = RetryConfig()
        
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    # Check if we should retry this exception
                    if should_retry and not should_retry(e):
                        raise
                    
                    # If this is the last attempt, don't retry
                    if attempt == config.max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {config.max_attempts} attempts: {e}")
                        raise
                    
                    # Calculate delay
                    delay = config.initial_delay * (config.backoff_multiplier ** attempt)
                    
                    # Cap delay at max_delay
                    delay = min(delay, config.max_delay)
                    
                    # Add jitter if enabled
                    if config.jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(
                        f"Attempt {attempt + 1} of {func.__name__} failed: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    # Special handling for rate limit errors
                    if isinstance(e, PubMedRateLimitError):
                        # For rate limit errors, use the delay from the API if available
                        # or use a longer delay
                        delay = max(delay, 5.0)
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
            
        return wrapper
    return decorator


def should_retry_pubmed_error(exception: Exception) -> bool:
    """
    Determine if a PubMed error should be retried.
    
    Args:
        exception: The exception to check
        
    Returns:
        True if the exception should be retried, False otherwise
    """
    # Don't retry on 404 or validation errors
    if isinstance(exception, (ValueError, TypeError)):
        return False
    
    # Don't retry on permanent API errors
    if hasattr(exception, 'status_code'):
        status_code = getattr(exception, 'status_code')
        if status_code and 400 <= status_code < 500 and status_code != 429:
            return False
    
    # Retry on network errors, rate limit errors, and server errors
    return isinstance(exception, (PubMedNetworkError, PubMedRateLimitError)) or (
        hasattr(exception, 'status_code') and 
        isinstance(getattr(exception, 'status_code'), int) and
        (getattr(exception, 'status_code') >= 500 or getattr(exception, 'status_code') == 429)
    )