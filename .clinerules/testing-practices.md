## Brief overview
Testing practices and guidelines for the Thai Traditional Medicine RAG Bot project, emphasizing comprehensive testing, ethical API usage, and proper test structure.

## Testing philosophy
- Test-driven development is the preferred approach
- Both unit tests and integration tests are required for all features
- Tests must respect ethical guidelines for external API usage
- All tests should pass before code is considered complete

## Unit testing approach
- Use pytest as the primary testing framework
- Use unittest.mock for mocking external dependencies
- Create reusable test objects using pytest fixtures
- Verify expected behavior with clear assertions
- Mock external API calls to avoid unnecessary network requests

## Integration testing guidelines
- Integration tests should use real APIs with respectful rate limiting
- Maximum 3 results per search query in tests
- Minimum 1 second between API requests
- Use pytest markers to distinguish integration tests from unit tests
- Tests should be configurable through environment variables

## Test structure
- Organize tests in tests/unit/ and tests/integration/ directories
- Name test files with test_ prefix
- Each test should have a clear docstring explaining what it tests
- Group related tests in test classes when appropriate

## Running tests
- Use `make test` for unit tests
- Use `make test-integration` for integration tests  
- Use `make test-cov` for tests with coverage report
- Run tests frequently during development

## Coverage requirements
- Aim for >80% test coverage for new code
- Critical paths should have 100% coverage
- Test both success and failure scenarios
- Include edge cases and error handling tests

## Ethical API usage
- Implement rate limiting in all external API tests
- Use minimal result sets to reduce API load
- Make minimum necessary API calls
- Use common, non-abusive search queries
- Respect API provider guidelines and terms of service
