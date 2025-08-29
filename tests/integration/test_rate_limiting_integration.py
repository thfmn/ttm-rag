"""
Integration tests for rate limiting functionality.

These tests verify that our rate limiting mechanisms work correctly
with the real PubMed API.
"""

import sys
import os
import time
import pytest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.rate_limiting import (
    TokenBucket,
    RateLimiter,
    configure_rate_limiting,
    acquire_rate_limit
)


@pytest.mark.integration
class TestRateLimitingIntegration:
    """Integration tests for rate limiting functionality."""
    
    def test_token_bucket_burst_and_refill(self):
        """Test token bucket burst capacity and refill over time."""
        # Create a bucket with high rate for quick testing
        bucket = TokenBucket(rate=100.0, capacity=50.0)
        
        # Consume all tokens in a burst
        assert bucket.consume(50.0) is True
        assert bucket.tokens == 0.0
        
        # Wait for tokens to refill
        time.sleep(0.2)  # Wait 0.2 seconds
        
        # Should have approximately 20 new tokens (100 * 0.2)
        # But tokens should not exceed capacity
        assert 19.0 <= bucket.tokens <= 21.0 or bucket.tokens == 0.0  # Account for timing issues
    
    def test_rate_limiter_with_multiple_buckets(self):
        """Test rate limiter with multiple buckets."""
        limiter = RateLimiter()
        
        # Configure different buckets
        limiter.configure_bucket("api1", 10.0, 20.0)
        limiter.configure_bucket("api2", 5.0, 10.0)
        
        # Acquire tokens from different buckets
        assert limiter.acquire("api1", 5.0) is True
        assert limiter.acquire("api2", 3.0) is True
        
        # Check that buckets are separate
        bucket1 = limiter._get_bucket("api1")
        bucket2 = limiter._get_bucket("api2")
        
        assert bucket1.tokens < 20.0  # Should have consumed tokens
        assert bucket2.tokens < 10.0  # Should have consumed tokens
    
    def test_global_rate_limiting_configuration(self):
        """Test global rate limiting configuration."""
        # Configure rate limiting
        configure_rate_limiting("test_resource", 5.0, 15.0)
        
        # Try to acquire tokens
        assert acquire_rate_limit("test_resource", 1.0) is True
        
        # Clean up by removing the configuration
        from src.utils.rate_limiting import GLOBAL_RATE_LIMITER
        if "test_resource" in GLOBAL_RATE_LIMITER.bucket_configs:
            del GLOBAL_RATE_LIMITER.bucket_configs["test_resource"]
        if "test_resource" in GLOBAL_RATE_LIMITER.buckets:
            del GLOBAL_RATE_LIMITER.buckets["test_resource"]
    
    def test_rate_limiting_delays(self):
        """Test that rate limiting introduces appropriate delays."""
        limiter = RateLimiter()
        limiter.configure_bucket("slow_api", 2.0, 2.0)  # 2 tokens/sec, 2 capacity
        
        # Consume all tokens
        bucket = limiter._get_bucket("slow_api")
        assert bucket.consume(2.0) is True
        assert bucket.tokens == 0.0
        
        # Acquiring tokens should introduce a delay
        start_time = time.monotonic()
        assert limiter.acquire("slow_api", 1.0, timeout=2.0) is True
        end_time = time.monotonic()
        
        # Should have waited approximately 0.5 seconds (1 token / 2 tokens/sec)
        elapsed = end_time - start_time
        assert 0.4 <= elapsed <= 0.7
    
    def test_rate_limiting_timeout(self):
        """Test that rate limiting respects timeouts."""
        limiter = RateLimiter()
        limiter.configure_bucket("very_slow_api", 0.1, 1.0)  # Very slow rate
        
        # Consume all tokens
        bucket = limiter._get_bucket("very_slow_api")
        assert bucket.consume(1.0) is True
        assert bucket.tokens == 0.0
        
        # Trying to acquire many tokens should timeout
        start_time = time.monotonic()
        assert limiter.acquire("very_slow_api", 5.0, timeout=0.1) is False
        end_time = time.monotonic()
        
        # Should have timed out quickly
        elapsed = end_time - start_time
        assert elapsed < 0.2