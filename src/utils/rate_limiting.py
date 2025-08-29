"""
Rate limiting utilities for the Thai Traditional Medicine RAG Bot.

This module provides utilities for implementing rate limiting to respect
API usage guidelines and prevent overwhelming external services.
"""

import time
import threading
from typing import Optional, Dict, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TokenBucket:
    """
    Token bucket rate limiter implementation.
    
    This implementation allows for flexible rate limiting with burst capacity.
    """
    
    def __init__(self, rate: float, capacity: float):
        """
        Initialize the token bucket.
        
        Args:
            rate: Tokens added per second (requests per second)
            capacity: Maximum number of tokens (burst capacity)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self.lock = threading.Lock()
    
    def consume(self, tokens: float = 1.0) -> bool:
        """
        Try to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if not enough tokens
        """
        with self.lock:
            # Add tokens based on time elapsed
            now = time.monotonic()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            # Try to consume tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def wait_time(self, tokens: float = 1.0) -> float:
        """
        Calculate time to wait until enough tokens are available.
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Time in seconds to wait until enough tokens are available
        """
        with self.lock:
            # Add tokens based on time elapsed
            now = time.monotonic()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            # If we have enough tokens, no wait needed
            if self.tokens >= tokens:
                return 0.0
            
            # Calculate wait time needed to accumulate enough tokens
            needed = tokens - self.tokens
            return needed / self.rate


class RateLimiter:
    """
    Rate limiter for API calls.
    
    Manages rate limiting for different resources or endpoints.
    """
    
    def __init__(self):
        """Initialize the rate limiter."""
        self.buckets: Dict[str, TokenBucket] = {}
        self.bucket_configs: Dict[str, Dict[str, float]] = {}
        self.default_config = {"rate": 1.0, "capacity": 10.0}  # 1 request/sec, 10 burst
        self.lock = threading.Lock()
    
    def configure_bucket(self, name: str, rate: float, capacity: float):
        """
        Configure a rate limiting bucket.
        
        Args:
            name: Name of the bucket
            rate: Tokens added per second
            capacity: Maximum number of tokens
        """
        with self.lock:
            self.bucket_configs[name] = {"rate": rate, "capacity": capacity}
            # Recreate bucket with new configuration
            if name in self.buckets:
                del self.buckets[name]
    
    def configure_default(self, rate: float, capacity: float):
        """
        Configure default rate limiting settings.
        
        Args:
            rate: Tokens added per second
            capacity: Maximum number of tokens
        """
        self.default_config = {"rate": rate, "capacity": capacity}
    
    def _get_bucket(self, name: str) -> TokenBucket:
        """
        Get or create a bucket for the given name.
        
        Args:
            name: Name of the bucket
            
        Returns:
            TokenBucket instance
        """
        with self.lock:
            if name not in self.buckets:
                # Use configured settings or defaults
                config = self.bucket_configs.get(name, self.default_config)
                self.buckets[name] = TokenBucket(config["rate"], config["capacity"])
            return self.buckets[name]
    
    def acquire(self, name: str, tokens: float = 1.0, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens from the rate limiter.
        
        Args:
            name: Name of the bucket
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait (None for no timeout)
            
        Returns:
            True if tokens were acquired, False if timeout exceeded
        """
        bucket = self._get_bucket(name)
        
        # Try to consume immediately
        if bucket.consume(tokens):
            return True
        
        # If we can't consume immediately, calculate wait time
        wait_time = bucket.wait_time(tokens)
        
        # If no timeout or wait time is within timeout, wait and try again
        if timeout is None or wait_time <= timeout:
            if wait_time > 0:
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s for {name}")
                time.sleep(wait_time)
            return bucket.consume(tokens)
        
        # Timeout exceeded
        return False
    
    async def async_acquire(self, name: str, tokens: float = 1.0, timeout: Optional[float] = None) -> bool:
        """
        Asynchronously acquire tokens from the rate limiter.
        
        Args:
            name: Name of the bucket
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait (None for no timeout)
            
        Returns:
            True if tokens were acquired, False if timeout exceeded
        """
        import asyncio
        
        bucket = self._get_bucket(name)
        
        # Try to consume immediately
        if bucket.consume(tokens):
            return True
        
        # If we can't consume immediately, calculate wait time
        wait_time = bucket.wait_time(tokens)
        
        # If no timeout or wait time is within timeout, wait and try again
        if timeout is None or wait_time <= timeout:
            if wait_time > 0:
                logger.debug(f"Rate limiting: asynchronously waiting {wait_time:.2f}s for {name}")
                await asyncio.sleep(wait_time)
            return bucket.consume(tokens)
        
        # Timeout exceeded
        return False


# Global rate limiter instance
GLOBAL_RATE_LIMITER = RateLimiter()


def configure_rate_limiting(resource: str, requests_per_second: float, burst_capacity: float):
    """
    Configure rate limiting for a specific resource.
    
    Args:
        resource: Name of the resource
        requests_per_second: Number of requests allowed per second
        burst_capacity: Maximum burst capacity
    """
    GLOBAL_RATE_LIMITER.configure_bucket(resource, requests_per_second, burst_capacity)


def configure_default_rate_limiting(requests_per_second: float, burst_capacity: float):
    """
    Configure default rate limiting settings.
    
    Args:
        requests_per_second: Number of requests allowed per second
        burst_capacity: Maximum burst capacity
    """
    GLOBAL_RATE_LIMITER.configure_default(requests_per_second, burst_capacity)


def acquire_rate_limit(resource: str, tokens: float = 1.0, timeout: Optional[float] = None) -> bool:
    """
    Acquire rate limit tokens for a resource.
    
    Args:
        resource: Name of the resource
        tokens: Number of tokens to acquire
        timeout: Maximum time to wait (None for no timeout)
        
    Returns:
        True if tokens were acquired, False if timeout exceeded
    """
    return GLOBAL_RATE_LIMITER.acquire(resource, tokens, timeout)


async def async_acquire_rate_limit(resource: str, tokens: float = 1.0, timeout: Optional[float] = None) -> bool:
    """
    Asynchronously acquire rate limit tokens for a resource.
    
    Args:
        resource: Name of the resource
        tokens: Number of tokens to acquire
        timeout: Maximum time to wait (None for no timeout)
        
    Returns:
        True if tokens were acquired, False if timeout exceeded
    """
    return await GLOBAL_RATE_LIMITER.async_acquire(resource, tokens, timeout)