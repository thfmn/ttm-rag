# Testing

Testing is a crucial part of our development process. We've implemented both unit tests and integration tests to ensure our code works correctly.

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

We've also created integration tests that verify our code works with the real PubMed API.

### Integration Test Structure

Our integration tests:

1. **Use real API**: Instead of mocking, these tests connect to the actual PubMed API
2. **Verify real data**: They check that we can correctly process real data from the API
3. **Are marked appropriately**: We use pytest markers to distinguish integration tests from unit tests

### Example Integration Test

Here's our integration test:

```python
@pytest.mark.integration
def test_pubmed_connector_integration():
    """Integration test for PubMed connector with real API"""
    # Create a source object
    source = Source(
        id=1,
        name="PubMed",
        type="academic",
        # ... other fields
    )
    
    # Create connector
    connector = PubMedConnector(source)
    
    # Test searching for articles
    pmids = connector.search_articles("traditional medicine", 5)
    
    # Assertions
    assert isinstance(pmids, list)
    assert len(pmids) <= 5
    
    # Test fetching article details
    if pmids:
        articles = connector.fetch_article_details([pmids[0]])
        assert isinstance(articles, list)
        assert len(articles) == 1
        # ... more assertions
```

This test verifies that our connector works correctly with the real PubMed API.

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
- **Integration Tests**: 1/1 passing

This gives us confidence that our implementation is working correctly.