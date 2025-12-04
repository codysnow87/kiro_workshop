# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Update backend/requirements.txt with necessary packages (boto3, mangum, pytest, hypothesis)
  - Create directory structure for models, services, repositories, and routers
  - Set up testing framework configuration
  - _Requirements: 8.1, 8.5_

- [x] 2. Implement data models and validation
  - Create Pydantic models for Event, CreateEventRequest, UpdateEventRequest
  - Implement field validation rules (non-empty strings, non-negative capacity, date format)
  - Add response models for API endpoints
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 2.1 Write property test for input validation
  - **Property 2: Input Validation Completeness**
  - **Validates: Requirements 1.2, 5.1, 5.2, 5.4, 5.6, 5.7, 6.3**

- [x] 2.2 Write property test for type validation
  - **Property 3: Type Validation**
  - **Validates: Requirements 1.3, 3.3, 5.2**

- [x] 2.3 Write property test for date format validation
  - **Property 4: Date Format Validation**
  - **Validates: Requirements 5.3**

- [x] 2.4 Write property test for capacity validation
  - **Property 5: Capacity Validation**
  - **Validates: Requirements 5.5**

- [x] 3. Implement DynamoDB repository layer
  - Create DynamoDBRepository class with boto3 client initialization
  - Implement put_item method for creating/updating events
  - Implement get_item method for retrieving events by eventId
  - Implement scan_items method for listing all events with optional filtering
  - Implement delete_item method for removing events
  - Add error handling for DynamoDB exceptions
  - _Requirements: 1.1, 2.1, 2.3, 3.1, 4.1_

- [x] 3.1 Write unit tests for repository methods
  - Test put_item with mocked DynamoDB
  - Test get_item with existing and non-existent items
  - Test scan_items with and without filters
  - Test delete_item operations
  - _Requirements: 1.1, 2.1, 2.3, 3.1, 4.1_

- [x] 4. Implement service layer
  - Create EventService class with repository dependency
  - Implement create_event method (generate eventId if not provided, validate, call repository)
  - Implement get_event method (retrieve from repository, handle not found)
  - Implement list_events method (with optional status filter)
  - Implement update_event method (partial updates, merge with existing data)
  - Implement delete_event method (call repository, handle not found)
  - _Requirements: 1.1, 1.4, 2.1, 2.2, 2.3, 2.5, 3.1, 3.2, 4.1, 4.2, 9.7_

- [x] 4.1 Write property test for create-retrieve round trip
  - **Property 1: Create-Retrieve Round Trip**
  - **Validates: Requirements 1.1, 1.4, 2.1**

- [x] 4.2 Write property test for client-provided eventId
  - **Property 13: Client-Provided EventId**
  - **Validates: Requirements 9.7**

- [x] 4.3 Write property test for list completeness
  - **Property 6: List Completeness**
  - **Validates: Requirements 2.3**

- [x] 4.4 Write property test for status filter correctness
  - **Property 7: Status Filter Correctness**
  - **Validates: Requirements 2.5**

- [x] 4.5 Write property test for update correctness
  - **Property 8: Update Correctness**
  - **Validates: Requirements 3.1, 3.4**

- [x] 4.6 Write property test for partial update preservation
  - **Property 9: Partial Update Preservation**
  - **Validates: Requirements 9.5**

- [x] 4.7 Write property test for delete removes event
  - **Property 10: Delete Removes Event**
  - **Validates: Requirements 4.1**

- [x] 4.8 Write property test for not found error handling
  - **Property 12: Not Found Error Handling**
  - **Validates: Requirements 2.2, 3.2, 4.2**

- [x] 5. Implement FastAPI routes
  - Create events router with all CRUD endpoints
  - Implement POST /events endpoint (call service, return 201 with created event)
  - Implement GET /events endpoint (with optional status query parameter)
  - Implement GET /events/{eventId} endpoint (return 200 or 404)
  - Implement PUT /events/{eventId} endpoint (partial updates, return 200 or 404)
  - Implement DELETE /events/{eventId} endpoint (return 200/204 or 404)
  - Add exception handlers for validation errors and not found errors
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.5, 3.1, 3.2, 3.3, 4.1, 4.2, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 5.1 Write property test for create success status
  - **Property 15: Create Success Status**
  - **Validates: Requirements 7.1, 9.3**

- [x] 5.2 Write property test for delete success status
  - **Property 11: Delete Success Status**
  - **Validates: Requirements 4.3**

- [x] 5.3 Write property test for error response format
  - **Property 14: Error Response Format**
  - **Validates: Requirements 6.4**

- [x] 6. Integrate FastAPI with Lambda handler
  - Update backend/main.py to include all routes
  - Add Mangum adapter for Lambda integration
  - Configure dependency injection for repository and service
  - Add environment variable handling for DynamoDB table name
  - _Requirements: 8.1, 8.4_

- [x] 6.1 Write integration tests for API endpoints
  - Test complete request/response flow for all endpoints
  - Test with FastAPI TestClient
  - Verify status codes and response formats
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [x] 7. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement infrastructure with AWS CDK
  - Create DynamoDB table construct in infrastructure/stacks/main_stack.py
  - Define table with eventId as partition key, on-demand billing
  - Create Lambda function construct with Python 3.11 runtime
  - Package FastAPI application code for Lambda deployment
  - Configure Lambda environment variables (table name, region)
  - Add IAM permissions for Lambda to access DynamoDB
  - _Requirements: 8.1, 8.2, 8.5_

- [x] 9. Add API Gateway integration
  - Create API Gateway REST API construct
  - Configure Lambda proxy integration
  - Set up CORS configuration
  - Define all API routes and methods
  - Output the API Gateway URL after deployment
  - _Requirements: 8.2, 8.3, 8.4_

- [x] 10. Add deployment documentation
  - Update infrastructure/README.md with deployment instructions
  - Document required AWS credentials and permissions
  - Add example commands for deploying and testing
  - Document how to retrieve the public API endpoint URL
  - _Requirements: 8.3, 8.5_

- [x] 11. Final Checkpoint - Deploy and verify
  - Ensure all tests pass, ask the user if questions arise.
  - Deploy the stack to AWS
  - Verify the public endpoint is accessible
  - Test all endpoints against the deployed API

