---
inclusion: fileMatch
fileMatchPattern: '**/routers/**/*.py|**/main.py|**/*api*.py'
---

# API Standards and Conventions

## REST API Conventions

### HTTP Methods
- **GET**: Retrieve resources (read-only, idempotent)
- **POST**: Create new resources
- **PUT**: Update/replace entire resources (idempotent)
- **PATCH**: Partially update resources
- **DELETE**: Remove resources (idempotent)

### HTTP Status Codes
Use appropriate status codes for all responses:

**Success Codes:**
- `200 OK`: Successful GET, PUT, PATCH, or DELETE
- `201 Created`: Successful POST that creates a resource
- `204 No Content`: Successful DELETE with no response body

**Client Error Codes:**
- `400 Bad Request`: Invalid request format or validation errors
- `404 Not Found`: Resource does not exist
- `409 Conflict`: Request conflicts with current state (e.g., duplicate resource)
- `422 Unprocessable Entity`: Valid format but semantic errors

**Server Error Codes:**
- `500 Internal Server Error`: Unexpected server errors
- `503 Service Unavailable`: Temporary service unavailability

### Error Response Format
All error responses MUST follow this standardized JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

Example error responses:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid event data provided",
    "details": {
      "field": "date",
      "issue": "Date must be in ISO 8601 format"
    }
  }
}
```

## JSON Response Format Standards

### Success Response Structure
All successful responses MUST return valid JSON with consistent structure:

**Single Resource:**
```json
{
  "id": "resource-id",
  "field1": "value1",
  "field2": "value2"
}
```

**Collection of Resources:**
```json
{
  "items": [
    {"id": "1", "field": "value"},
    {"id": "2", "field": "value"}
  ],
  "count": 2
}
```

### Field Naming Conventions
- Use `snake_case` for JSON field names
- Use descriptive, clear field names
- Avoid abbreviations unless widely understood
- Be consistent across all endpoints

### Date and Time Format
- Use ISO 8601 format for all dates and timestamps
- Example: `"2024-03-15T14:30:00Z"`

### Response Headers
- Always set `Content-Type: application/json` for JSON responses
- Include appropriate CORS headers when needed

## API Implementation Guidelines

### Validation
- Validate all input data before processing
- Return `400 Bad Request` with detailed error messages for validation failures
- Use Pydantic models for request/response validation

### Error Handling
- Catch and handle all exceptions appropriately
- Never expose internal error details or stack traces to clients
- Log detailed errors server-side for debugging
- Return user-friendly error messages in responses

### Documentation
- Document all endpoints with clear descriptions
- Include request/response examples
- Document all possible error responses
- Keep API documentation up to date
