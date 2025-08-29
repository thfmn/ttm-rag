**API Design Study Guide**

---

### 1. Understanding APIs
- **Definition:** Application Programming Interface (API) defines how software components should interact.
- **Role in System Architecture:** Acts as a contract between client and server, specifying request methods, endpoints, responses.
- **Key Functions:**
  - Abstraction: Hides implementation details.
  - Service Boundaries: Defines clear interfaces between systems.

---

### 2. API Styles
- **REST (Representational State Transfer):**
  - Resource-based, uses HTTP methods (GET, POST, PUT, PATCH, DELETE).
  - Stateless: Each request contains all info needed.
  - Common in web/mobile apps.
  - URL example: `/api/v1/users/123`
- **GraphQL:**
  - Single endpoint, client specifies exact data needed.
  - Uses schema, queries, mutations, subscriptions.
  - No versioning; schema evolves without breaking clients.
  - Efficient for complex UIs with nested data.
- **gRPC:**
  - High-performance RPC framework.
  - Uses Protocol Buffers.
  - Supports streaming and bidirectional communication.
  - Ideal for microservices and internal server communication.

---

### 3. API Design Principles
- **Consistency:** Use uniform naming conventions and patterns.
- **Simplicity:** Focus on core use cases; intuitive design.
- **Security:** Implement authentication, authorization, input validation, rate limiting.
- **Performance:** Use caching, pagination, minimize payloads, reduce round trips.

---

### 4. Protocols & Their Influence
- **HTTP/HTTPS:**
  - Foundation for REST APIs.
  - HTTPS adds encryption (TLS/SSL).
  - Use status codes for response status.
- **WebSockets:**
  - Enable real-time, bidirectional communication.
  - Suitable for chat, live updates.
- **Message Queuing Protocols (AMQP):**
  - Asynchronous messaging, reliable delivery.
  - Used in event-driven architectures.
- **gRPC:**
  - Uses HTTP/2.
  - Efficient for server-to-server communication.

---

### 5. API Design Process
- **Requirements Gathering:** Identify core use cases, user stories.
- **Scope & Boundaries:** Define features to develop now vs. later.
- **Performance & Security Constraints:** Plan for bottlenecks, security needs.
- **Design Approaches:**
  - Top-down: Start from high-level requirements.
  - Bottom-up: Use existing data models.
  - Contract-first: Define API contract before implementation.
- **Lifecycle:**
  - Design → Develop → Deploy → Monitor → Maintain → Deprecate

---

### 6. RESTful API Design
- **Resource Modeling:**
  - Use nouns (e.g., `/products`, `/orders`).
  - Resources can be collections or individual items.
  - Nested resources: `/products/{id}/reviews`.
- **Filtering, Sorting, Pagination:**
  - Filtering: `/products?category=electronics&in_stock=true`
  - Sorting: `/products?sort=price&order=asc`
  - Pagination: `/products?page=2&limit=10` or `/products?offset=20&limit=10`
- **HTTP Methods:**
  - GET: Read data.
  - POST: Create resource.
  - PUT: Replace resource.
  - PATCH: Partially update resource.
  - DELETE: Remove resource.
- **Status Codes:**
  - 200 OK, 201 Created, 204 No Content
  - 400 Bad Request, 401 Unauthorized, 404 Not Found
  - 500 Internal Server Error
- **Best Practices:**
  - Use plural nouns.
  - Proper HTTP methods.
  - Version APIs (`/api/v1/`).
  - Consistent URL patterns.

---

### 7. GraphQL API Design
- **Schema & Types:**
  - Define types (e.g., `User`, `Post`).
  - Queries for fetching data.
  - Mutations for modifying data.
- **Queries & Mutations:**
  - Clients specify exactly what data they need.
  - Example query: `{ user(id: 1) { name, posts { title } } }`
  - Example mutation: `createUser(input: { name: "John" }) { id, name }`
- **Error Handling:**
  - Always returns HTTP 200.
  - Errors are in the `errors` field.
- **Best Practices:**
  - Keep schemas small and modular.
  - Limit query depth.
  - Use meaningful naming.
  - Use input types for mutations.

---

### 8. Authentication & Authorization
- **Authentication:**
  - Verifies identity.
  - Types:
    - Basic Auth (username/password, insecure without HTTPS).
    - Bearer tokens (JWT, stateless).
    - OAuth2 (delegated access, third-party login).
    - SSO (Single Sign-On, e.g., via OAuth2/OIDC).
- **Authorization:**
  - Determines what actions/resources a user can access.
  - Models:
    - Role-Based Access Control (RBAC): roles like admin, user.
    - Attribute-Based Access Control (ABAC): based on user/resource attributes.
    - Access Control Lists (ACL): resource-specific permissions.
  - Enforced via tokens, policies, or ACLs.

---

### 9. Security Best Practices
- **Rate Limiting:** Prevent abuse by limiting requests per user/IP.
- **CORS:** Restrict which domains can access your API.
- **Input Validation:** Prevent injection attacks.
- **Firewalls & WAFs:** Block malicious traffic.
- **VPNs:** Restrict internal APIs.
- **CSRF Tokens:** Prevent cross-site request forgery.
- **XSS Prevention:** Sanitize user input to prevent script injection.

---

### 10. Protocols & Transport Layer
- **TCP:** Reliable, ordered delivery; used in REST, gRPC.
- **UDP:** Faster, unreliable; used in real-time apps like gaming, video streaming.
- **HTTP/2:** Used by gRPC for performance.
- **Transport Layer Choice:** Depends on latency, reliability, security needs.

---

### 11. Summary & Next Steps
- Master core API styles: REST, GraphQL, gRPC.
- Follow best practices for resource modeling, versioning, security.
- Understand protocols and transport layers.
- Practice designing and implementing APIs.
- Consider mentorship or real-world projects to deepen understanding.

---

### 12. Additional Resources
- **Mentorship Program:** For hands-on experience and career advancement.
- **Next Lesson:** Deep dive into API protocols and their strengths/limitations.

---

**Remember:** Building effective APIs requires understanding both design principles and underlying protocols. Practice, real-world application, and continuous learning are key to mastering API development and moving into senior roles.

---

**End of Study Guide**
