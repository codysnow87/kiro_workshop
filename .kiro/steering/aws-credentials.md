---
inclusion: always
---

# AWS Credentials Management

## Terminal Session Persistence

When running AWS CLI commands or CDK operations:
- ALWAYS reuse existing terminal sessions instead of creating new ones
- If AWS credentials are needed and not available, prompt the user to provide them
- Never assume credentials are available - check first and ask if needed

## Credential Handling

Before running AWS-related commands:
1. Check if AWS credentials are configured in the current session
2. If credentials are missing, ask the user: "AWS credentials are needed. Please provide your AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_SESSION_TOKEN (if applicable), or let me know if you'd like to configure them differently."
3. Wait for user input before proceeding

## Commands Requiring AWS Credentials

These operations require valid AWS credentials:
- `aws` CLI commands
- `cdk deploy`, `cdk synth`, `cdk diff`
- Any boto3-based Python scripts
- DynamoDB local or remote operations
- Any infrastructure deployment or testing

## Best Practices

- Remind users to never commit credentials to version control
- Suggest using environment variables or AWS credential files
- Recommend AWS SSO or temporary credentials for enhanced security
