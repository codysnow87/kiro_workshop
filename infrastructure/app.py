#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.main_stack import MainStack

app = cdk.App()

# Get environment from AWS CLI configuration
env = cdk.Environment(
    account=os.environ.get('CDK_DEFAULT_ACCOUNT'),
    region=os.environ.get('CDK_DEFAULT_REGION', 'us-west-2')
)

MainStack(app, "MainStack", env=env)

app.synth()
