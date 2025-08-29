"""
Unit tests for rate limiting utilities.

These tests verify that our rate limiting mechanisms work correctly.
"""

import sys
import os
import time
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.rate_limiting import (
    TokenBucket,
    RateLimiter,
    configure_rate_limiting,
    configure_default_rate_limiting,
    acquire_rate_limit,
    async_acquire_rate_limit,
    GLOBAL_RATE_LIMITER
)


class TestTokenBucket:
    """Tests for the TokenBucket class."""
    
    def test_token_bucket_initialization(self):
        """Test initializing a token bucket."""
        bucket = TokenBucket(rate=1.0, capacity=10.0)
        assert bucket.rate == 1.0
        assert bucket.capacity == 10.0
        assert bucket.tokens == 10.0
    
    def test_token_bucket_consume_immediate(self):
        """Test consuming tokens immediately."""
        bucket = TokenBucket(rate=1.0, capacity=10.0)
        
        # Should be able to consume tokens immediately
        assert bucket.consume(1.0) is True
        assert abs(bucket.tokens - 9.0) < 0.0001
        
        # Should be able to consume multiple tokens
        assert bucket.consume(2.0) is True
        assert abs(bucket.tokens - 7.0) < 0.0001
        
        # Should not be able to consume more tokens than available
        assert bucket.consume(8.0) is False
        assert abs(bucket.tokens - 7.0) < 0.0001  # Tokens should remain unchanged
    
    def test_token_bucket_refill_over_time(self):
        """Test that tokens refill over time."""
        bucket = TokenBucket(rate=10.0, capacity=10.0)  # 10 tokens/sec
        
        # Consume all tokens
        assert bucket.consume(10.0) is True
        assert bucket.tokens == 0.0
        
        # Wait for tokens to refill
        time.sleep(0.5)  # Wait 0.5 seconds
        
        # Should be able to consume some tokens now
        assert bucket.consume(4.0) is True
        # Should have approximately 1 token left (5 created - 4 consumed)
        assert abs(bucket.tokens - 1.0) < 0.1
    
    def test_token_bucket_wait_time(self):
        """Test calculating wait time."""
        bucket = TokenBucket(rate=1.0, capacity=10.0)  # 1 token/sec
        
        # Consume all tokens
        assert bucket.consume(10.0) is True
        assert bucket.tokens == 0.0
        
        # Should need to wait 5 seconds to get 5 tokens
        wait_time = bucket.wait_time(5.0)
        assert abs(wait_time - 5.0) < 0.1
        
        # Should need to wait 10 seconds to get all tokens back
        wait_time = bucket.wait_time(10.0)
        assert abs(wait_time - 10.0) < 0.1
        
        # Should not need to wait if we have enough tokens
        bucket.tokens = 5.0
        wait_time = bucket.wait_time(3.0)
        assert wait_time == 0.0


class TestRateLimiter:
    """Tests for the RateLimiter class."""
    
    def test_rate_limiter_initialization(self):
        """Test initializing a rate limiter."""
        limiter = RateLimiter()
        assert len(limiter.buckets) == 0
        assert len(limiter.bucket_configs) == 0
        assert limiter.default_config == {"rate": 1.0, "capacity": 10.0}
    
    def test_rate_limiter_configure_bucket(self):
        """Test configuring a bucket."""
        limiter = RateLimiter()
        limiter.configure_bucket("test", 5.0, 20.0)
        
        assert "test" in limiter.bucket_configs
        assert limiter.bucket_configs["test"] == {"rate": 5.0, "capacity": 20.0}
    
    def test_rate_limiter_configure_default(self):
        """Test configuring default settings."""
        limiter = RateLimiter()
        limiter.configure_default(2.0, 15.0)
        
        assert limiter.default_config == {"rate": 2.0, "capacity": 15.0}
    
    def test_rate_limiter_get_bucket(self):
        """Test getting a bucket."""
        limiter = RateLimiter()
        
        # First call should create a new bucket
        bucket1 = limiter._get_bucket("test")
        assert bucket1 is not None
        
        # Second call should return the same bucket
        bucket2 = limiter._get_bucket("test")
        assert bucket1 is bucket2
    
    def test_rate_limiter_acquire_immediate(self):
        """Test acquiring tokens immediately."""
        limiter = RateLimiter()
        limiter.configure_bucket("test", 10.0, 10.0)  # High rate for immediate acquisition
        
        # Should be able to acquire tokens immediately
        assert limiter.acquire("test", 1.0) is True
    
    def test_rate_limiter_acquire_wait(self):
        """Test acquiring tokens with waiting."""
        limiter = RateLimiter()
        limiter.configure_bucket("test", 10.0, 10.0)  # High rate for quick acquisition
        
        # Consume all tokens
        bucket = limiter._get_bucket("test")
        assert bucket.consume(10.0) is True
        
        # Should wait and then acquire tokens
        start_time = time.monotonic()
        assert limiter.acquire("test", 5.0, timeout=1.0) is True
        end_time = time.monotonic()
        
        # Should have waited a short time
        assert end_time - start_time < 1.0
    
    def test_rate_limiter_acquire_timeout(self):
        """Test acquiring tokens with timeout exceeded."""
        limiter = RateLimiter()
        limiter.configure_bucket("test", 0.1, 1.0)  # Very slow rate
        
        # Consume all tokens
        bucket = limiter._get_bucket("test")
        assert bucket.consume(1.0) is True
        
        # Should timeout trying to acquire many tokens
        assert limiter.acquire("test", 5.0, timeout=0.1) is False


# Tests for global functions
class TestGlobalFunctions:
    """Tests for global rate limiting functions."""
    
    def test_configure_rate_limiting(self):
        """Test configuring rate limiting."""
        # Clear any existing configuration
        GLOBAL_RATE_LIMITER.bucket_configs.clear()
        
        configure_rate_limiting("test_resource", 5.0, 15.0)
        
        assert "test_resource" in GLOBAL_RATE_LIMITER.bucket_configs
        assert GLOBAL_RATE_LIMITER.bucket_configs["test_resource"] == {"rate": 5.0, "capacity": 15.0}
    
    def test_configure_default_rate_limiting(self):
        """Test configuring default rate limiting."""
        original_config = GLOBAL_RATE_LIMITER.default_config.copy()
        
        configure_default_rate_limiting(3.0, 12.0)
        
        assert GLOBAL_RATE_LIMITER.default_config == {"rate": 3.0, "capacity": 12.0}
        
        # Restore original config
        GLOBAL_RATE_LIMITER.default_config = original_config
    
    def test_acquire_rate_limit(self):
        """Test acquiring rate limit tokens."""
        # Configure a high-rate bucket for testing
        GLOBAL_RATE_LIMITER.configure_bucket("test_acquire", 100.0, 100.0)
        
        # Should be able to acquire tokens immediately
        assert acquire_rate_limit("test_acquire", 1.0) is True
    
    @pytest.mark.asyncio
    async def test_async_acquire_rate_limit(self):
        """Test asynchronously acquiring rate limit tokens."""
        # Configure a high-rate bucket for testing
        GLOBAL_RATE_LIMITER.configure_bucket("test_async_acquire", 100.0, 100.0)
        
        # Should be able to acquire tokens immediately
        assert await async_acquire_rate_limit("test_async_acquire", 1.0) is True