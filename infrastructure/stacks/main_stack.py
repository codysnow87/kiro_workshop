import os
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_apigateway as apigateway,
    Duration,
    CfnOutput,
)
from constructs import Construct


class MainStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create DynamoDB table for events
        events_table = dynamodb.Table(
            self,
            "EventsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=self._get_removal_policy(),
        )
        
        # Create Lambda function for the FastAPI application
        from aws_cdk import BundlingOptions
        api_lambda = lambda_.Function(
            self,
            "EventManagementApiLambda",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="main.handler",
            architecture=lambda_.Architecture.X86_64,
            code=lambda_.Code.from_asset(
                path=os.path.join(os.path.dirname(__file__), "../../backend"),
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_11.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        "pip install -r requirements.txt --platform manylinux2014_x86_64 --only-binary=:all: -t /asset-output && "
                        "cp -r . /asset-output"
                    ],
                )
            ),
            environment={
                "DYNAMODB_TABLE_NAME": events_table.table_name,
            },
            timeout=Duration.seconds(30),
            memory_size=512,
        )
        
        # Grant Lambda permissions to access DynamoDB table
        events_table.grant_read_write_data(api_lambda)
        
        # Create API Gateway REST API
        api = apigateway.RestApi(
            self,
            "EventManagementApi",
            rest_api_name="Event Management API",
            description="REST API for Event Management System",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=[
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                ],
                allow_credentials=False,
            ),
        )
        
        # Create Lambda integration
        lambda_integration = apigateway.LambdaIntegration(
            api_lambda,
            proxy=True,
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    },
                )
            ],
        )
        
        # Define API routes
        # GET /events - List all events
        events_resource = api.root.add_resource("events")
        events_resource.add_method(
            "GET",
            lambda_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    },
                )
            ],
        )
        
        # POST /events - Create a new event
        events_resource.add_method(
            "POST",
            lambda_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="201",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    },
                )
            ],
        )
        
        # GET /events/{eventId} - Get a specific event
        event_resource = events_resource.add_resource("{eventId}")
        event_resource.add_method(
            "GET",
            lambda_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    },
                )
            ],
        )
        
        # PUT /events/{eventId} - Update an event
        event_resource.add_method(
            "PUT",
            lambda_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    },
                )
            ],
        )
        
        # DELETE /events/{eventId} - Delete an event
        event_resource.add_method(
            "DELETE",
            lambda_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    },
                )
            ],
        )
        
        # Output the API Gateway URL
        CfnOutput(
            self,
            "ApiGatewayUrl",
            value=api.url,
            description="URL of the Event Management API Gateway endpoint"
        )
        
        # Output the Lambda function ARN
        CfnOutput(
            self,
            "LambdaFunctionArn",
            value=api_lambda.function_arn,
            description="ARN of the Event Management API Lambda function"
        )
        
        # Output the DynamoDB table name
        CfnOutput(
            self,
            "DynamoDBTableName",
            value=events_table.table_name,
            description="Name of the Events DynamoDB table"
        )
    
    def _get_removal_policy(self):
        """Get removal policy based on environment"""
        from aws_cdk import RemovalPolicy
        # For development, we can destroy the table
        # For production, you might want to use RETAIN
        return RemovalPolicy.DESTROY
