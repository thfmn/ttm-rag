"""
Configuration for integration tests.

This file contains settings that control how our integration tests
interact with external services like the PubMed API.
"""

import os

class IntegrationTestConfig:
    """Configuration class for integration tests"""
    
    # Rate limiting settings
    MIN_REQUEST_INTERVAL = float(os.getenv('INTEGRATION_TEST_MIN_INTERVAL', '1.0'))  # seconds
    
    # Maximum results per search to minimize API load
    MAX_SEARCH_RESULTS = int(os.getenv('INTEGRATION_TEST_MAX_RESULTS', '3'))
    
    # Maximum number of articles to fetch details for
    MAX_FETCH_ARTICLES = int(os.getenv('INTEGRATION_TEST_MAX_FETCH', '3'))
    
    # Test query to use for basic functionality tests
    TEST_QUERY = os.getenv('INTEGRATION_TEST_QUERY', 'traditional medicine')
    
    # Timeout for API requests (seconds)
    REQUEST_TIMEOUT = int(os.getenv('INTEGRATION_TEST_TIMEOUT', '30'))
    
    # Whether to skip integration tests (for CI environments without external access)
    SKIP_INTEGRATION_TESTS = os.getenv('SKIP_INTEGRATION_TESTS', 'false').lower() == 'true'
    
    # Maximum number of requests allowed per test to prevent abuse
    MAX_REQUESTS_PER_TEST = int(os.getenv('INTEGRATION_TEST_MAX_REQUESTS', '5'))