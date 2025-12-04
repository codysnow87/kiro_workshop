# Event Management API - Backend

A serverless REST API built with FastAPI for managing events. The API provides full CRUD operations for event management with data persistence in AWS DynamoDB. Designed to run on AWS Lambda with API Gateway for automatic scaling and high availability.

## Features

- **Full CRUD Operations**: Create, read, update, and delete events
- **Event Filtering**: Filter events by status
- **Partial Updates**: Update only specific fields without affecting others
- **Data Validation**: Comprehensive input validation using Pydantic
- **Serverless Architecture**: Runs on AWS Lambda for automatic scaling
- **Property-Based Testing**: Extensive test coverage using Hypothesis
- **RESTful Design**: Follows REST conventions with proper HTTP status codes

## Prerequisites

- **Python**: 3.11 or higher
- **pip**: Latest version recommended
- **Virtual Environment**: Recommended for dependency isolation
- **AWS Account**: Required for deployment (DynamoDB access)
- **Docker**: Required for CDK deployment (Lambda bundling)

## Installation

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies Overview

The `requirements.txt` includes:
- **fastapi** (0.115.0): Modern web framework for building APIs
- **uvicorn** (0.32.0): ASGI server for running FastAPI
- **pydantic** (2.9.0): Data validation using Python type annotations
- **boto3** (1.35.0): AWS SDK for Python (DynamoDB operations)
- **mangum** (0.18.0): ASGI adapter for AWS Lambda
- **pytest** (8.3.0): Testing framework
- **hypothesis** (6.115.0): Property-based testing library
- **moto** (5.0.0): AWS service mocking for tests
- **httpx** (0.27.0): HTTP client for testing

## Configuration

### Environment Variables

The application uses the following environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DYNAMODB_TABLE_NAME` | Name of the DynamoDB table for events | Yes | `events` |
| `AWS_REGION` | AWS region (auto-set by Lambda runtime) | No | Auto-detected |

### Local Development

For local development, you can set environment variables:

```bash
export DYNAMODB_TABLE_NAME=events
```

Or create a `.env` file (not committed to git):

```env
DYNAMODB_TABLE_NAME=events
```

### AWS Deployment

When deployed via CDK, environment variables are automatically configured in the Lambda function.

## Running Locally

### Development Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Using DynamoDB Local (Optional)

For local testing with DynamoDB:

```bash
# Install DynamoDB Local
docker run -p 8000:8000 amazon/dynamodb-local

# Update boto3 endpoint in code to point to localhost:8000
```

## API Documentation

### Base URL

**Production**: `https://m4vehfzim8.execute-api.us-west-2.amazonaws.com/prod/`

**Local**: `http://localhost:8000`

### Endpoints

#### Create Event
```http
POST /events
Content-Type: application/json

{
  "title": "Tech Conference 2024",
  "description": "Annual technology conference",
  "date": "2024-12-15",
  "location": "San Francisco",
  "capacity": 500,
  "organizer": "Tech Corp",
  "status": "scheduled"
}
```

**Response** (201 Created):
```json
{
  "eventId": "614b345c-5114-4788-bd81-f792d59463b5",
  "title": "Tech Conference 2024",
  "description": "Annual technology conference",
  "date": "2024-12-15",
  "location": "San Francisco",
  "capacity": 500,
  "organizer": "Tech Corp",
  "status": "scheduled"
}
```

#### List All Events
```http
GET /events
```

**Response** (200 OK):
```json
[
  {
    "eventId": "614b345c-5114-4788-bd81-f792d59463b5",
    "title": "Tech Conference 2024",
    ...
  }
]
```

#### Filter Events by Status
```http
GET /events?status=scheduled
```

#### Get Specific Event
```http
GET /events/{eventId}
```

**Response** (200 OK or 404 Not Found)

#### Update Event
```http
PUT /events/{eventId}
Content-Type: application/json

{
  "status": "cancelled",
  "capacity": 600
}
```

**Response** (200 OK): Returns updated event with all fields

#### Delete Event
```http
DELETE /events/{eventId}
```

**Response** (200 OK):
```json
{
  "message": "Event {eventId} deleted successfully"
}
```

### Status Codes

- `200 OK`: Successful GET, PUT, DELETE
- `201 Created`: Successful POST
- `404 Not Found`: Resource doesn't exist
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Usage Examples

### Using cURL

```bash
# Create an event
curl -X POST https://m4vehfzim8.execute-api.us-west-2.amazonaws.com/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Workshop",
    "description": "Python workshop",
    "date": "2024-11-20",
    "location": "Online",
    "capacity": 50,
    "organizer": "Python Community",
    "status": "active"
  }'

# List all events
curl https://m4vehfzim8.execute-api.us-west-2.amazonaws.com/prod/events

# Filter by status
curl "https://m4vehfzim8.execute-api.us-west-2.amazonaws.com/prod/events?status=active"

# Get specific event
curl https://m4vehfzim8.execute-api.us-west-2.amazonaws.com/prod/events/{eventId}

# Update event
curl -X PUT https://m4vehfzim8.execute-api.us-west-2.amazonaws.com/prod/events/{eventId} \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Delete event
curl -X DELETE https://m4vehfzim8.execute-api.us-west-2.amazonaws.com/prod/events/{eventId}
```

### Using Python

```python
import requests

BASE_URL = "https://m4vehfzim8.execute-api.us-west-2.amazonaws.com/prod"

# Create event
response = requests.post(
    f"{BASE_URL}/events",
    json={
        "title": "Tech Meetup",
        "description": "Monthly tech meetup",
        "date": "2024-12-01",
        "location": "Seattle",
        "capacity": 100,
        "organizer": "Tech Community",
        "status": "scheduled"
    }
)
event = response.json()
print(f"Created event: {event['eventId']}")

# List events
response = requests.get(f"{BASE_URL}/events")
events = response.json()
print(f"Total events: {len(events)}")

# Update event
response = requests.put(
    f"{BASE_URL}/events/{event['eventId']}",
    json={"status": "cancelled"}
)
updated_event = response.json()
print(f"Updated status: {updated_event['status']}")
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Types

```bash
# Unit tests only
pytest tests/unit/ -v

# Property-based tests only
pytest tests/unit/test_*_properties.py -v

# Integration tests
pytest tests/integration/ -v
```

### Test Coverage

The test suite includes:
- **Unit Tests**: Test individual components (models, services, repositories)
- **Property-Based Tests**: Verify correctness properties across random inputs using Hypothesis
- **Integration Tests**: Test complete request/response flows

### Property-Based Testing

The application uses Hypothesis for property-based testing to verify:
- Create-retrieve round trips
- Input validation completeness
- Partial update preservation
- Status filter correctness
- Error handling consistency

Each property test runs 100 iterations with randomly generated data.

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── models/
│   └── event.py           # Pydantic models for events
├── services/
│   └── event_service.py   # Business logic layer
├── repositories/
│   └── dynamodb_repository.py  # Data access layer
├── routers/
│   └── events.py          # API route definitions
├── tests/
│   ├── unit/              # Unit and property tests
│   └── integration/       # Integration tests
├── requirements.txt       # Python dependencies
└── pytest.ini            # Pytest configuration
```

## Deployment

The backend is deployed as part of the infrastructure stack. See `../infrastructure/README.md` for deployment instructions.

### Quick Deployment

```bash
cd ../infrastructure
cdk deploy
```

The CDK stack will:
1. Create a DynamoDB table for events
2. Package the FastAPI application with dependencies
3. Deploy a Lambda function with the application
4. Create an API Gateway REST API
5. Configure IAM permissions
6. Output the public API endpoint URL

## Troubleshooting

### Common Issues

#### Import Errors

**Problem**: `ModuleNotFoundError` when running the application

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### DynamoDB Connection Issues

**Problem**: `Unable to locate credentials` or DynamoDB access errors

**Solution**: 
- For local development: Configure AWS credentials (`aws configure`)
- For Lambda: Ensure IAM role has DynamoDB permissions (handled by CDK)

#### Port Already in Use

**Problem**: `Address already in use` when starting uvicorn

**Solution**: Use a different port or kill the existing process:
```bash
uvicorn main:app --reload --port 8001
```

#### Validation Errors

**Problem**: 422 status code when creating/updating events

**Solution**: Check the error response for details. Common issues:
- Missing required fields (title, description, date, location, capacity, organizer, status)
- Invalid data types (capacity must be integer)
- Negative capacity values
- Invalid date format (use YYYY-MM-DD)

#### Lambda Cold Start Issues

**Problem**: First request to deployed API is slow

**Solution**: This is normal Lambda behavior. Subsequent requests will be faster. Consider:
- Using provisioned concurrency for production
- Implementing Lambda warming strategies

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Locally with Mocked AWS

```bash
# Tests automatically use moto for AWS mocking
pytest tests/ -v
```

## Architecture

The backend follows a layered architecture:

1. **API Layer** (`routers/`): Handles HTTP requests, validation, and responses
2. **Service Layer** (`services/`): Implements business logic and orchestration
3. **Repository Layer** (`repositories/`): Abstracts data access to DynamoDB
4. **Model Layer** (`models/`): Defines data structures and validation rules

This separation enables:
- Easy testing with mocked dependencies
- Clear separation of concerns
- Flexibility to change data storage without affecting business logic

## Related Documentation

- **Infrastructure**: See `../infrastructure/README.md` for deployment and AWS resources
- **API Specification**: See `.kiro/specs/event-management-api/design.md` for detailed design
- **Requirements**: See `.kiro/specs/event-management-api/requirements.md` for feature requirements

## Contributing

When adding new features:
1. Update the requirements document
2. Add corresponding tests (unit and property-based)
3. Implement the feature following the layered architecture
4. Update this README with new endpoints or configuration
5. Run all tests to ensure nothing breaks

## License

See LICENSE file in the project root.
