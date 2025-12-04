# Event Management API

A serverless REST API for managing events, built with FastAPI and deployed on AWS using infrastructure as code. The application provides full CRUD operations with automatic scaling, high availability, and comprehensive testing.

## 🚀 Live Demo

**API Endpoint**: `https://m4vehfzim8.execute-api.us-west-2.amazonaws.com/prod/`

Try it out:
```bash
# Create an event
curl -X POST https://m4vehfzim8.execute-api.us-west-2.amazonaws.com/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Meetup",
    "description": "Monthly tech meetup",
    "date": "2024-12-01",
    "location": "Seattle",
    "capacity": 100,
    "organizer": "Tech Community",
    "status": "scheduled"
  }'

# List all events
curl https://m4vehfzim8.execute-api.us-west-2.amazonaws.com/prod/events
```

## 📋 Features

- ✅ **Full CRUD Operations**: Create, read, update, and delete events
- ✅ **Event Filtering**: Filter events by status
- ✅ **Partial Updates**: Update specific fields without affecting others
- ✅ **Data Validation**: Comprehensive input validation using Pydantic
- ✅ **Serverless Architecture**: Auto-scaling with AWS Lambda
- ✅ **Property-Based Testing**: Extensive test coverage with Hypothesis
- ✅ **Infrastructure as Code**: Reproducible deployments with AWS CDK
- ✅ **RESTful Design**: Follows REST conventions with proper HTTP status codes

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   Client    │─────▶│ API Gateway  │─────▶│   Lambda    │─────▶│  DynamoDB    │
│  (Browser/  │      │   (REST API) │      │  (FastAPI)  │      │   (Events)   │
│   cURL)     │◀─────│              │◀─────│             │◀─────│              │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
```

### Components

- **API Gateway**: Routes HTTP requests and handles CORS
- **Lambda Function**: Runs the FastAPI application (Python 3.11)
- **DynamoDB**: NoSQL database for event storage (on-demand billing)
- **CloudWatch**: Logs and monitoring

## 📁 Project Structure

```
.
├── backend/                    # FastAPI application
│   ├── main.py                # Application entry point
│   ├── models/                # Pydantic data models
│   ├── services/              # Business logic layer
│   ├── repositories/          # Data access layer
│   ├── routers/               # API route definitions
│   ├── tests/                 # Unit, property, and integration tests
│   └── requirements.txt       # Python dependencies
│
├── infrastructure/            # AWS CDK infrastructure
│   ├── app.py                # CDK application entry point
│   ├── stacks/               # CDK stack definitions
│   │   └── main_stack.py     # Main infrastructure stack
│   └── requirements.txt      # CDK dependencies
│
└── .kiro/specs/              # Feature specifications
    └── event-management-api/
        ├── requirements.md   # Feature requirements
        ├── design.md         # System design
        └── tasks.md          # Implementation tasks
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for AWS CDK)
- AWS Account with configured credentials
- Docker (for CDK deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the development server**
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

### Deploy to AWS

1. **Install AWS CDK**
   ```bash
   npm install -g aws-cdk
   ```

2. **Configure AWS credentials**
   ```bash
   aws configure
   ```

3. **Bootstrap CDK (first time only)**
   ```bash
   cd infrastructure
   cdk bootstrap
   ```

4. **Deploy the stack**
   ```bash
   pip install -r requirements.txt
   cdk deploy
   ```

5. **Get your API endpoint**
   The deployment will output your API Gateway URL:
   ```
   Outputs:
   MainStack.ApiGatewayUrl = https://xxxxxxxxxx.execute-api.us-west-2.amazonaws.com/prod/
   ```

## 📖 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/events` | Create a new event |
| GET | `/events` | List all events |
| GET | `/events?status={status}` | Filter events by status |
| GET | `/events/{eventId}` | Get a specific event |
| PUT | `/events/{eventId}` | Update an event |
| DELETE | `/events/{eventId}` | Delete an event |

### Event Model

```json
{
  "eventId": "string (auto-generated UUID)",
  "title": "string (required)",
  "description": "string (required)",
  "date": "string (required, YYYY-MM-DD format)",
  "location": "string (required)",
  "capacity": "integer (required, >= 0)",
  "organizer": "string (required)",
  "status": "string (required)"
}
```

### Example Requests

See detailed examples in:
- [Backend README](backend/README.md) - Complete API documentation
- [Infrastructure README](infrastructure/README.md) - Deployment and testing

## 🧪 Testing

### Run All Tests

```bash
cd backend
pytest tests/ -v
```

### Test Coverage

- **Unit Tests**: Test individual components
- **Property-Based Tests**: Verify correctness across random inputs (100 iterations each)
- **Integration Tests**: Test complete request/response flows

### Property-Based Testing

The application uses Hypothesis to verify correctness properties:
- Create-retrieve round trips
- Input validation completeness
- Partial update preservation
- Status filter correctness
- Error handling consistency

## 📚 Documentation

- **[Backend README](backend/README.md)**: Detailed API documentation, usage examples, and troubleshooting
- **[Infrastructure README](infrastructure/README.md)**: Deployment guide, AWS resources, and monitoring
- **[Design Document](.kiro/specs/event-management-api/design.md)**: System architecture and design decisions
- **[Requirements](.kiro/specs/event-management-api/requirements.md)**: Feature requirements and acceptance criteria

## 🛠️ Technology Stack

### Backend
- **FastAPI** (0.115.0): Modern Python web framework
- **Pydantic** (2.9.0): Data validation
- **Boto3** (1.35.0): AWS SDK for Python
- **Mangum** (0.18.0): ASGI adapter for Lambda
- **Hypothesis** (6.115.0): Property-based testing

### Infrastructure
- **AWS CDK** (2.114.1): Infrastructure as code
- **AWS Lambda**: Serverless compute
- **API Gateway**: REST API management
- **DynamoDB**: NoSQL database
- **CloudWatch**: Logging and monitoring

### Testing
- **Pytest** (8.3.0): Testing framework
- **Moto** (5.0.0): AWS service mocking
- **HTTPX** (0.27.0): HTTP client for testing

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DYNAMODB_TABLE_NAME` | DynamoDB table name | `events` |

### AWS Resources

After deployment, the following resources are created:
- DynamoDB table with on-demand billing
- Lambda function (512 MB memory, 30s timeout)
- API Gateway REST API with CORS enabled
- IAM roles with least-privilege permissions
- CloudWatch log groups

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**AWS Credentials**
```bash
# Configure AWS CLI
aws configure

# Verify credentials
aws sts get-caller-identity
```

**Docker Not Running**
```bash
# Start Docker Desktop and verify
docker ps
```

See detailed troubleshooting guides in:
- [Backend Troubleshooting](backend/README.md#troubleshooting)
- [Infrastructure Troubleshooting](infrastructure/README.md#troubleshooting)

## 📊 Monitoring

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/MainStack-EventManagementApiLambda* --follow

# View recent errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/MainStack-EventManagementApiLambda* \
  --filter-pattern "ERROR"
```

### Metrics

Monitor in AWS CloudWatch:
- Lambda invocations, errors, duration
- API Gateway request count, latency, 4xx/5xx errors
- DynamoDB read/write operations, throttling

## 🧹 Cleanup

To remove all AWS resources:

```bash
cd infrastructure
cdk destroy
```

**Warning**: This will delete the DynamoDB table and all event data.

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Review the [requirements](.kiro/specs/event-management-api/requirements.md) and [design](.kiro/specs/event-management-api/design.md)
2. Add tests for new features (unit and property-based)
3. Follow the layered architecture pattern
4. Update documentation
5. Ensure all tests pass

## 📞 Support

For issues or questions:
1. Check the troubleshooting sections in the READMEs
2. Review CloudWatch logs for error details
3. Consult the design and requirements documents

## 🎯 Development Workflow

1. **Local Development**: Make changes and test locally with `uvicorn`
2. **Run Tests**: Verify with `pytest tests/ -v`
3. **Preview Changes**: Use `cdk diff` to see infrastructure changes
4. **Deploy**: Run `cdk deploy` to update AWS resources
5. **Monitor**: Check CloudWatch logs and metrics
6. **Iterate**: Repeat as needed

---

Built with ❤️ using FastAPI, AWS CDK, and modern serverless architecture.
