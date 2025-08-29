# Internal Onboarding Summary

## Overview

This document provides a summary of the security and monitoring features implemented in the Thai Traditional Medicine RAG Bot project for new team members.

## Key Security Features Implemented

### 1. Input Sanitization
- **Purpose**: Prevent XSS attacks and injection vulnerabilities
- **Library**: nh3 (Python binding for ammonia HTML sanitizer)
- **Location**: `src/api/sanitization.py`
- **Usage**: Automatically applied to all API endpoints
- **Functions**: `sanitize_text()`, `sanitize_query()`, `sanitize_list()`

### 2. Audit Logging
- **Purpose**: Compliance tracking and security monitoring
- **Location**: `src/api/audit.py`
- **Features**: 
  - General event logging
  - HTTP request logging
  - Data access logging
  - Security event logging with severity levels
- **Storage**: `audit.log` file in development

### 3. Data Encryption
- **Purpose**: Protect sensitive metadata
- **Library**: cryptography
- **Location**: `src/utils/encryption.py`
- **Features**:
  - String encryption/decryption
  - Dictionary encryption/decryption
  - Key management
- **Configuration**: Uses `ENCRYPTION_KEY` environment variable

### 4. HTTPS Enforcement
- **Purpose**: Ensure secure communication in production
- **Location**: `src/api/security.py`
- **Activation**: When `ENVIRONMENT=production` and `HTTPS_ENABLED=true`

### 5. CORS Configuration
- **Purpose**: Control cross-origin requests
- **Location**: `src/api/main.py`
- **Configuration**: Currently allows all origins (restrict in production)

## Monitoring and Observability

### 1. Prometheus Metrics
- **Library**: prometheus-client
- **Location**: `src/api/monitoring.py`
- **Metrics Collected**:
  - HTTP request count and duration
  - Active requests
  - Error rates

### 2. Health Check Endpoints
- **Endpoints**:
  - `/health` - Basic health status
  - `/metrics` - Prometheus metrics

## Documentation

### 1. Comprehensive Onboarding Guide
- **Location**: `docs/onboarding.md`
- **Content**: Detailed instructions for using all security features

### 2. API Practices Study Guide
- **Location**: `docs/api_practices.md`
- **Content**: Comprehensive guide on API design principles, security, authentication, and best practices
- **Coverage**: REST, GraphQL, gRPC, security patterns, authentication methods

### 3. Deployment Guide
- **Location**: `docs/deployment.md`
- **Content**: Instructions for local, Docker, and production deployment

## Testing

### 1. Security Feature Testing
- All security features are covered by unit tests
- Located in `tests/unit/test_api.py`

### 2. Running Tests
```bash
make test          # Run all tests
make test-cov      # Run tests with coverage report
```

## Configuration

### Environment Variables
```bash
# Security
ENCRYPTION_KEY=your_base64_encoded_key_here
ENVIRONMENT=development|production
HTTPS_ENABLED=true|false

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# API Keys
PUBMED_API_KEY=your_pubmed_api_key
```

## Best Practices for New Team Members

### 1. Always Sanitize User Input
```python
from src.api.sanitization import sanitize_text, sanitize_query, sanitize_list

# Sanitize all user inputs
clean_name = sanitize_text(user_input)
```

### 2. Add Audit Logging to New Endpoints
```python
from src.api.audit import AuditLogger

@app.post("/new-endpoint")
async def new_endpoint(request: Request):
    AuditLogger.log_request(request)
    # ... endpoint logic
```

### 3. Encrypt Sensitive Data
```python
from src.utils.encryption import encrypt_sensitive_data, decrypt_sensitive_data

# Encrypt before storage
encrypted_data = encrypt_sensitive_data(sensitive_info)
```

### 4. Add Custom Metrics When Needed
```python
from prometheus_client import Counter

CUSTOM_EVENTS = Counter('custom_events_total', 'Total custom events')

def my_function():
    CUSTOM_EVENTS.inc()
    # ... function logic
```

## Quick Links

- [Onboarding Guide](http://localhost:8081/onboarding.html)
- [Deployment Guide](http://localhost:8081/deployment.html)
- [API Documentation](http://localhost:8081/index.html)
- [Health Check Endpoint](http://localhost:8005/health)
- [Metrics Endpoint](http://localhost:8005/metrics)

## Next Steps

1. Review the full onboarding guide for detailed implementation examples
2. Run the test suite to understand how security features are validated
3. Examine existing endpoints to see how security features are integrated
4. Check the deployment guide for production configuration details
