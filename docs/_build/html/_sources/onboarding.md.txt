# Internal Onboarding Guide

This guide provides detailed instructions for new team members on how to use the security and monitoring features implemented in the Thai Traditional Medicine RAG Bot project.

## Table of Contents
1. [Security Features](#security-features)
2. [Monitoring and Metrics](#monitoring-and-metrics)
3. [Audit Logging](#audit-logging)
4. [Data Encryption](#data-encryption)
5. [HTTPS Enforcement](#https-enforcement)
6. [CORS Configuration](#cors-configuration)
7. [API Design and Best Practices](#api-design-and-best-practices)

## Security Features

### Input Sanitization

The application implements input sanitization to prevent XSS attacks and other injection vulnerabilities using the `nh3` library (Python binding for the ammonia HTML sanitizer).

#### How to Use

Input sanitization is automatically applied to all API endpoints. The sanitization functions are located in `src/api/sanitization.py`:

```python
from src.api.sanitization import sanitize_text, sanitize_query, sanitize_list

# Sanitize a single text input
clean_text = sanitize_text("<script>alert('XSS')</script>Hello World")
# Result: "Hello World"

# Sanitize a search query
clean_query = sanitize_query("medicine<script>alert('XSS')</script>")
# Result: "medicine"

# Sanitize a list of items
clean_list = sanitize_list(["item1<script>", "item2"])
# Result: ["item1", "item2"]
```

#### Adding Sanitization to New Endpoints

When creating new API endpoints, ensure you sanitize all user inputs:

```python
from src.api.sanitization import sanitize_text, sanitize_query, sanitize_list

@app.get("/new-endpoint")
async def new_endpoint(
    name: str = Query(..., description="User name"),
    tags: List[str] = Query([], description="Tags")
):
    # Sanitize inputs
    clean_name = sanitize_text(name)
    clean_tags = sanitize_list(tags)
    
    # Use sanitized inputs in your logic
    # ...
```

### Audit Logging

The application implements comprehensive audit logging for compliance tracking. Logs are stored in `audit.log` during development and can be configured for production environments.

#### How to Use

Audit logging is implemented in `src/api/audit.py`. The `AuditLogger` class provides several methods for logging different types of events:

```python
from src.api.audit import AuditLogger
from fastapi import Request

# Log a general event
AuditLogger.log_event(
    event_type="user_action",
    user="john_doe",
    ip_address="192.168.1.1",
    details={"action": "data_export", "record_count": 100}
)

# Log an HTTP request
AuditLogger.log_request(request, user="john_doe")

# Log data access
AuditLogger.log_data_access(
    data_type="pubmed_articles",
    action="search",
    user="john_doe",
    ip_address="192.168.1.1",
    record_count=10
)

# Log a security event
AuditLogger.log_security_event(
    event_type="failed_login",
    description="Failed login attempt for user john_doe",
    user="john_doe",
    ip_address="192.168.1.1",
    severity="high"
)
```

#### Adding Audit Logging to New Endpoints

When creating new API endpoints, add audit logging:

```python
from src.api.audit import AuditLogger

@app.post("/sensitive-operation")
async def sensitive_operation(request: Request, user: str):
    # Log the request
    AuditLogger.log_request(request, user=user)
    
    try:
        # Perform the operation
        result = perform_sensitive_operation()
        
        # Log successful data access
        AuditLogger.log_data_access(
            data_type="sensitive_data",
            action="access",
            user=user,
            ip_address=request.client.host if request.client else None,
            record_count=1
        )
        
        return result
    except Exception as e:
        # Log security event
        AuditLogger.log_security_event(
            event_type="operation_failed",
            description=f"Operation failed: {str(e)}",
            user=user,
            ip_address=request.client.host if request.client else None,
            severity="high"
        )
        raise
```

### Data Encryption

The application provides data encryption utilities for protecting sensitive metadata using the `cryptography` library.

#### How to Use

Data encryption is implemented in `src/utils/encryption.py`. The `DataEncryption` class provides methods for encrypting and decrypting strings and dictionaries:

```python
from src.utils.encryption import DataEncryption, encrypt_sensitive_data, decrypt_sensitive_data

# Create an encryption instance
encryptor = DataEncryption()

# Encrypt a string
encrypted_text = encryptor.encrypt_string("sensitive data")
decrypted_text = encryptor.decrypt_string(encrypted_text)

# Or use the global utility functions
encrypted_text = encrypt_sensitive_data("sensitive data")
decrypted_text = decrypt_sensitive_data(encrypted_text)

# Encrypt a dictionary
sensitive_data = {"api_key": "secret123", "password": "mypassword"}
encrypted_dict = encryptor.encrypt_dict(sensitive_data)
decrypted_dict = encryptor.decrypt_dict(encrypted_dict)

# Get the encryption key (for storage/configuration)
key = encryptor.get_key()
```

#### Configuration

The encryption utility automatically uses an environment variable `ENCRYPTION_KEY` if available. If not, it generates a new key (which should be stored securely in production):

```bash
# Set the encryption key in your environment
export ENCRYPTION_KEY="your_base64_encoded_key_here"
```

#### Adding Encryption to New Components

When storing sensitive data, use encryption:

```python
from src.utils.encryption import encrypt_sensitive_data, decrypt_sensitive_data

class DatabaseConfig:
    def __init__(self):
        self.encrypted_credentials = None
    
    def store_credentials(self, username, password):
        # Encrypt sensitive data before storage
        credentials = {"username": username, "password": password}
        self.encrypted_credentials = encrypt_sensitive_data(str(credentials))
    
    def get_credentials(self):
        # Decrypt sensitive data when needed
        if self.encrypted_credentials:
            decrypted = decrypt_sensitive_data(self.encrypted_credentials)
            # Parse the decrypted string back to a dictionary
            import ast
            return ast.literal_eval(decrypted)
        return None
```

## Monitoring and Metrics

The application implements comprehensive monitoring using Prometheus metrics and provides health check endpoints.

### Prometheus Metrics

Metrics are automatically collected for all HTTP requests. The following metrics are available:

- `http_requests_total`: Total HTTP requests by method, endpoint, and status code
- `http_request_duration_seconds`: HTTP request duration by method and endpoint
- `http_active_requests`: Number of active HTTP requests
- `http_errors_total`: Total HTTP errors by method, endpoint, and error type

### Health Check Endpoints

The application provides two health check endpoints:

1. `/health` - Basic health check
2. `/metrics` - Prometheus metrics endpoint

#### Using the Health Check Endpoints

```bash
# Check application health
curl http://localhost:8000/health

# Get Prometheus metrics
curl http://localhost:8000/metrics
```

### Adding Custom Metrics

To add custom metrics to your components:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define custom metrics
CUSTOM_COUNTER = Counter('custom_events_total', 'Total custom events')
CUSTOM_HISTOGRAM = Histogram('custom_operation_duration_seconds', 'Duration of custom operations')
CUSTOM_GAUGE = Gauge('custom_active_operations', 'Number of active custom operations')

# Use the metrics in your code
def custom_operation():
    CUSTOM_GAUGE.inc()
    with CUSTOM_HISTOGRAM.time():
        # Perform operation
        result = perform_operation()
        CUSTOM_COUNTER.inc()
    CUSTOM_GAUGE.dec()
    return result
```

## HTTPS Enforcement

The application includes middleware to enforce HTTPS in production environments.

### How It Works

The `HTTPSMiddleware` in `src/api/security.py` automatically redirects HTTP requests to HTTPS when:
1. The environment variable `ENVIRONMENT` is set to "production"
2. The environment variable `HTTPS_ENABLED` is set to "true"

### Configuration

To enable HTTPS enforcement in production:

```bash
export ENVIRONMENT="production"
export HTTPS_ENABLED="true"
```

## CORS Configuration

Cross-Origin Resource Sharing (CORS) is configured to allow requests from any origin during development. In production, you should restrict this to specific origins.

### Configuration

The CORS middleware is configured in `src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
```

### Production Configuration

For production, restrict the allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
```

## Testing Security Features

All security features are tested in the unit test suite. To run the tests:

```bash
# Run all tests
make test

# Run only API tests
pytest tests/unit/test_api.py

# Run tests with coverage
make test-cov
```

### Adding Tests for Security Features

When adding new endpoints or features, include tests for security:

```python
def test_new_endpoint_with_xss_input(client):
    """Test that the new endpoint sanitizes XSS input."""
    response = client.get("/new-endpoint?name=<script>alert('XSS')</script>")
    assert response.status_code == 200
    # Verify that the response does not contain the script tag
    assert "<script>" not in response.text

def test_new_endpoint_audit_logging(client, mocker):
    """Test that the new endpoint logs audit events."""
    # Mock the audit logger
    mock_audit = mocker.patch('src.api.audit.AuditLogger.log_request')
    
    response = client.get("/new-endpoint")
    
    # Verify that audit logging was called
    mock_audit.assert_called_once()
```

## Best Practices

### 1. Always Sanitize User Input
Never trust user input. Always sanitize text, queries, and lists using the provided sanitization functions.

### 2. Log Security-Relevant Events
Log all security-relevant events, including failed authentication attempts, unauthorized access, and data access events.

### 3. Encrypt Sensitive Data
Always encrypt sensitive data before storing it, including API keys, passwords, and personal information.

### 4. Monitor for Anomalies
Regularly review metrics and logs for unusual patterns that might indicate security issues.

### 5. Keep Dependencies Updated
Regularly update security-related dependencies like `nh3`, `cryptography`, and `fastapi`.

### 6. Use Environment Variables for Secrets
Never hardcode sensitive information like encryption keys or API secrets in the code.

## API Design and Best Practices

For comprehensive guidance on API design, our project includes a detailed API practices study guide that covers modern API development principles and patterns.

### Key API Design Areas Covered

#### 1. API Architecture Styles
- **REST APIs**: Resource-based design with HTTP methods
- **GraphQL**: Query-based APIs for flexible data fetching  
- **gRPC**: High-performance RPC for microservices

#### 2. Security and Authentication
- **Authentication Methods**: Basic Auth, Bearer tokens, OAuth2, SSO
- **Authorization Models**: RBAC, ABAC, ACL patterns
- **Security Best Practices**: Rate limiting, input validation, CORS

#### 3. Design Principles
- **Consistency**: Uniform naming and patterns
- **Performance**: Caching, pagination, payload optimization
- **Maintainability**: Versioning, documentation, testing

### FastAPI Implementation Examples

Our project uses FastAPI which aligns with modern API best practices:

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

# RESTful endpoint design
@app.get("/api/v1/articles/{article_id}")
async def get_article(article_id: str):
    """Get a specific article by ID - follows REST conventions"""
    # Implementation follows resource-based URL design
    
# Input validation with Pydantic
class SearchRequest(BaseModel):
    query: str
    max_results: int = 10
    
@app.post("/api/v1/search")
async def search_articles(request: SearchRequest):
    """Search articles with validated input"""
    # Automatic request validation and serialization
```

### API Security Integration

Our security features align with API security best practices:

```python
# Rate limiting for API endpoints
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Implements token bucket rate limiting
    
# Input sanitization for all endpoints
@app.post("/api/v1/articles")
async def create_article(article_data: dict):
    # Automatic sanitization of user inputs
    sanitized_data = sanitize_dict(article_data)
```

### Reference Documentation

For detailed study of API design principles, authentication patterns, and implementation strategies, refer to:

- **[API Practices Study Guide](api_practices.html)** - Comprehensive guide covering API design principles, security patterns, and best practices
- **[Implementation Guide](implementation.html)** - Project-specific implementation details
- **[Security Guide](#security-features)** - Security features and their usage (above sections)

### Best Practices for API Development

When developing new API endpoints in this project:

1. **Follow RESTful conventions** for resource URLs and HTTP methods
2. **Use Pydantic models** for request/response validation
3. **Implement proper error handling** with meaningful HTTP status codes
4. **Add rate limiting** for resource-intensive endpoints
5. **Include audit logging** for security-sensitive operations
6. **Sanitize all inputs** to prevent injection attacks
7. **Document endpoints** with OpenAPI/Swagger annotations

### Quick Reference Links

- [API Practices Full Guide](api_practices.html) - Complete API design study guide
- [OpenAPI Documentation](http://localhost:8000/docs) - Live API documentation
- [Health Check Endpoint](http://localhost:8000/health) - API health status
- [Metrics Endpoint](http://localhost:8000/metrics) - Performance metrics
