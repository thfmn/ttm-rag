# Testing

Testing is a crucial part of our development process. We've implemented both unit tests and integration tests to ensure our code works correctly while respecting ethical guidelines for API usage.

## Unit Testing

We've created comprehensive unit tests for our PubMed connector and pipeline using pytest and unittest.mock.

### Test Structure

Our unit tests follow a clear structure:

1. **Fixtures**: We use pytest fixtures to create reusable test objects
2. **Mocking**: We use unittest.mock to mock external dependencies like the requests library
3. **Assertions**: We use pytest's assertion system to verify expected behavior

### Connector Tests

We've implemented tests for all key functionality of our PubMed connector:

1. **test_search_articles**: Verifies that the search function correctly returns article IDs
2. **test_search_articles_empty_result**: Tests the behavior when no articles are found
3. **test_search_articles_request_exception**: Tests error handling when the API request fails
4. **test_fetch_article_details**: Verifies that article details are correctly fetched
5. **test_fetch_article_details_empty_input**: Tests the behavior with empty input
6. **test_fetch_article_details_request_exception**: Tests error handling when fetching details fails

### Pipeline Tests

We've also implemented tests for our PubMed pipeline:

1. **test_pubmed_pipeline_run**: Tests the complete pipeline execution
2. **test_pubmed_pipeline_run_no_results**: Tests the pipeline behavior when no articles are found
3. **test_pubmed_pipeline_run_limited_results**: Tests the pipeline with a limited number of results

### Example Test

Here's an example of one of our unit tests:

```python
@patch('src.connectors.pubmed.requests.get')
def test_search_articles(mock_get, pubmed_connector):
    """Test searching for articles"""
    # Mock the response
    mock_response = Mock()
    mock_response.json.return_value = {
        "esearchresult": {
            "idlist": ["123456", "789012"]
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Test the method
    pmids = pubmed_connector.search_articles("traditional medicine", 10)
    
    # Assertions
    assert len(pmids) == 2
    assert "123456" in pmids
    assert "789012" in pmids
    mock_get.assert_called_once()
```

This test verifies that our search function correctly processes the API response and returns the expected article IDs.

## Integration Testing

We've also created comprehensive integration tests that verify our code works with the real PubMed API while following ethical guidelines:

### Ethical Considerations

Our integration tests are designed with the following ethical principles:

1. **Rate Limiting**: All tests implement respectful rate limiting to avoid overloading the PubMed API
2. **Minimal Requests**: Tests use small result sets (maximum 3 results) to minimize API load
3. **Controlled Usage**: Tests are designed to make the minimum number of API calls necessary
4. **Respectful Queries**: Tests use common, non-abusive search queries

### Test Structure

Our integration tests:

1. **Use real API**: Instead of mocking, these tests connect to the actual PubMed API
2. **Verify real data**: They check that we can correctly process real data from the API
3. **Follow ethical guidelines**: All tests implement rate limiting and minimal usage
4. **Are marked appropriately**: We use pytest markers to distinguish integration tests from unit tests

### Comprehensive Test Coverage

Our new integration test suite includes tests for:

1. **Basic Search Functionality**: Verifies the search_articles method works correctly
2. **Edge Cases**: Tests handling of empty queries and queries with no results
3. **Single Article Fetching**: Tests fetching details for a single article
4. **Multiple Article Fetching**: Tests fetching details for multiple articles
5. **Empty Input Handling**: Tests behavior with empty input lists
6. **Invalid Input Handling**: Tests behavior with invalid PMIDs
7. **Combined Workflows**: Tests the complete search-and-fetch workflow
8. **Different Query Types**: Tests various types of search queries
9. **Ethical Usage Verification**: Tests that we're using the API respectfully

### Example Integration Test

Here's an example of one of our integration tests:

```python
def test_search_and_fetch_combined(self, pubmed_connector):
    """Test combined search and fetch workflow"""
    # Rate limiting for search
    rate_limited_request()
    
    # Search for articles
    search_query = "medicinal plants"
    pmids = pubmed_connector.search_articles(search_query, 2)
    
    # Verify search results
    assert isinstance(pmids, list)
    assert len(pmids) <= 2
    
    # If we have results, fetch details
    if pmids:
        # Rate limiting for fetch
        rate_limited_request()
        
        articles = pubmed_connector.fetch_article_details(pmids)
        
        # Verify fetch results
        assert isinstance(articles, list)
        assert len(articles) == len(pmids)
        
        # Verify article structure
        for article in articles:
            assert "pmid" in article
            assert "raw_xml" in article
            assert article["pmid"] in pmids
            assert isinstance(article["raw_xml"], str)
            assert len(article["raw_xml"]) > 0
```

This test verifies that our connector can successfully search for articles and then fetch details for those articles, all while respecting rate limits.

### Configuration

Our integration tests are configurable through environment variables:

- `INTEGRATION_TEST_MIN_INTERVAL`: Minimum time between requests (default: 1.0 seconds)
- `INTEGRATION_TEST_MAX_RESULTS`: Maximum results per search (default: 3)
- `INTEGRATION_TEST_MAX_FETCH`: Maximum articles to fetch details for (default: 3)
- `INTEGRATION_TEST_QUERY`: Test query to use (default: "traditional medicine")
- `INTEGRATION_TEST_TIMEOUT`: Request timeout in seconds (default: 30)
- `SKIP_INTEGRATION_TESTS`: Whether to skip integration tests (default: false)
- `INTEGRATION_TEST_MAX_REQUESTS`: Maximum requests per test (default: 5)

## Running Tests

We've set up convenient commands in our Makefile to run tests:

```bash
# Run unit tests
make test

# Run integration tests
make test-integration

# Run tests with coverage
make test-cov
```

## Test Results

All our tests are currently passing:

- **Unit Tests**: 9/9 passing
- **Integration Tests**: 11/11 passing

This gives us confidence that our implementation is working correctly while respecting ethical guidelines for API usage.