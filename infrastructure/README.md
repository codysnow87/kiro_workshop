# Infrastructure

AWS CDK project for deploying the Event Management API to AWS using infrastructure as code.

## Prerequisites

- Python 3.11 or higher
- Node.js 18.x or higher (for AWS CDK CLI)
- AWS CLI configured with appropriate credentials
- AWS CDK CLI installed globally: `npm install -g aws-cdk`

## Required AWS Credentials and Permissions

### AWS Account Setup

You need an AWS account with programmatic access configured. Set up your credentials using one of these methods:

**Option 1: AWS CLI Configuration**
```bash
aws configure
```

**Option 2: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Option 3: AWS Profile**
```bash
export AWS_PROFILE=your-profile-name
```

### Required IAM Permissions

The AWS credentials must have permissions to create and manage the following resources:

- **CloudFormation**: Create, update, and delete stacks
- **Lambda**: Create functions, update code, manage execution roles
- **API Gateway**: Create REST APIs, configure integrations
- **DynamoDB**: Create tables, configure settings
- **IAM**: Create and attach roles and policies
- **S3**: Upload Lambda deployment packages (CDK bootstrap bucket)

**Recommended Policy**: `AdministratorAccess` for initial deployment, or create a custom policy with the specific permissions listed above.

### CDK Bootstrap

Before first deployment, bootstrap your AWS environment:

```bash
cdk bootstrap aws://ACCOUNT-ID/REGION
```

Replace `ACCOUNT-ID` with your AWS account ID and `REGION` with your target region (e.g., `us-east-1`).

## Setup

1. Install Python dependencies:
```bash
cd infrastructure
pip install -r requirements.txt
```

2. Verify CDK installation:
```bash
cdk --version
```

## Deployment

### Deploy the Stack

Deploy the complete Event Management API infrastructure:

```bash
cd infrastructure
cdk deploy
```

The deployment will:
1. Create a DynamoDB table for storing events
2. Package and deploy the FastAPI Lambda function
3. Create an API Gateway REST API
4. Configure IAM roles and permissions
5. Output the public API endpoint URL

**Note**: You will be prompted to approve IAM changes and security-related modifications. Review and confirm by typing `y`.

### Deploy with Auto-Approval

To skip confirmation prompts (useful for CI/CD):

```bash
cdk deploy --require-approval never
```

### View Changes Before Deployment

To see what changes will be made without deploying:

```bash
cdk diff
```

### List All Stacks

```bash
cdk ls
```

### Synthesize CloudFormation Template

To generate the CloudFormation template without deploying:

```bash
cdk synth
```

## Retrieving the Public API Endpoint URL

After successful deployment, the API Gateway endpoint URL will be displayed in the terminal output:

```
Outputs:
EventManagementStack.ApiEndpoint = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
```

### Retrieve Endpoint from AWS Console

1. Go to AWS Console → API Gateway
2. Select the Event Management API
3. Click "Stages" → "prod"
4. Copy the "Invoke URL"

### Retrieve Endpoint Using AWS CLI

```bash
aws cloudformation describe-stacks \
  --stack-name EventManagementStack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

## Testing the Deployed API

### Test Event Creation

```bash
curl -X POST https://YOUR-API-ENDPOINT/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Conference 2024",
    "description": "Annual technology conference",
    "date": "2024-12-15",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Corp",
    "status": "scheduled"
  }'
```

### Test List All Events

```bash
curl https://YOUR-API-ENDPOINT/events
```

### Test Get Specific Event

```bash
curl https://YOUR-API-ENDPOINT/events/{eventId}
```

### Test Update Event

```bash
curl -X PUT https://YOUR-API-ENDPOINT/events/{eventId} \
  -H "Content-Type: application/json" \
  -d '{
    "status": "cancelled"
  }'
```

### Test Delete Event

```bash
curl -X DELETE https://YOUR-API-ENDPOINT/events/{eventId}
```

### Test with Status Filter

```bash
curl https://YOUR-API-ENDPOINT/events?status=scheduled
```

## Monitoring and Logs

### View Lambda Logs

```bash
aws logs tail /aws/lambda/EventManagementFunction --follow
```

### View API Gateway Logs

Enable logging in API Gateway console, then:

```bash
aws logs tail /aws/apigateway/EventManagementApi --follow
```

### CloudWatch Metrics

Monitor the following in AWS CloudWatch:
- Lambda invocations, errors, and duration
- API Gateway request count and latency
- DynamoDB read/write capacity and throttling

## Cleanup

To remove all deployed resources:

```bash
cd infrastructure
cdk destroy
```

**Warning**: This will delete the DynamoDB table and all event data. Ensure you have backups if needed.

## Troubleshooting

### Deployment Fails with "No Default VPC"

CDK requires a default VPC. Create one or specify a VPC in the stack configuration.

### Lambda Function Timeout

If operations are timing out, increase the Lambda timeout in `stacks/main_stack.py`:

```python
timeout=Duration.seconds(60)
```

### DynamoDB Throttling

If you experience throttling, consider switching from on-demand to provisioned capacity with auto-scaling.

### CORS Issues

Ensure CORS is properly configured in the API Gateway settings if accessing from a web browser.

## Development Workflow

1. Make changes to infrastructure code in `stacks/main_stack.py`
2. Run `cdk diff` to preview changes
3. Run `cdk deploy` to apply changes
4. Test the updated API endpoints
5. Monitor CloudWatch logs for any issues

## Additional Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
