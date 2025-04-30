#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from saketrail_cdk.stacks.frontend_stack import FrontendStack

app = App()

# Common environment configuration
env = Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "ap-northeast-1")
)

# Staging environment
FrontendStack(
    app,
    "SakeTrailFrontendStaging",
    environment="staging",
    domain_name="saketrail.com",
    hosted_zone_id=os.getenv("HOSTED_ZONE_ID", ""),
    env=env,
)

# Production environment
FrontendStack(
    app,
    "SakeTrailFrontendProduction",
    environment="production",
    domain_name="saketrail.com",
    hosted_zone_id=os.getenv("HOSTED_ZONE_ID", ""),
    env=env,
)

app.synth() 