#!/usr/bin/env python3
import os
import yaml
from aws_cdk import App, Environment
from saketrail_cdk.stacks.frontend_stack import FrontendStack
from saketrail_cdk.stacks.auth_stack import AuthStack
from saketrail_cdk.stacks.api_stack import ApiStack
from saketrail_cdk.stacks.ai_label_recognition_stack import AiLabelRecognitionStack

app = App()

def load_config(env_name):
    config_path = os.path.join(os.path.dirname(__file__), f'../config/{env_name}.yml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# dev環境
config_dev = load_config('dev')
# prod環境
config_prod = load_config('prod')

env = Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "ap-northeast-1")
)

# AuthStack (dev)
auth_stack_dev = AuthStack(
    app,
    "SakeTrailAuthDev",
    environment="dev",
    env=env,
)

# FrontendStack (dev)
if "frontend" in config_dev:
    FrontendStack(
        app,
        "SakeTrailFrontendDev",
        environment="dev",
        domain_name=config_dev["frontend"]["domain"],
        certificate_arn=config_dev["frontend"]["certificate_arn"],
        env=env,
    )

# AuthStack (prod)
auth_stack_prod = AuthStack(
    app,
    "SakeTrailAuthProduction",
    environment="production",
    env=env,
)

# FrontendStack (prod)
FrontendStack(
    app,
    "SakeTrailFrontendProduction",
    environment="production",
    domain_name=config_prod["frontend"]["domain"],
    certificate_arn=config_prod["frontend"]["certificate_arn"],
    env=env,
)

# AiLabelRecognitionStack (dev)
ai_label_stack_dev = AiLabelRecognitionStack(
    app,
    "SakeTrailAiLabelRecognitionDev",
    environment="dev",
    env=env,
)

# AiLabelRecognitionStack (prod)
ai_label_stack_prod = AiLabelRecognitionStack(
    app,
    "SakeTrailAiLabelRecognitionProduction",
    environment="production",
    env=env,
)

# ApiStack (dev)
ApiStack(
    app,
    "SakeTrailApiDev",
    bucket=ai_label_stack_dev.bucket,  # dev用S3バケットリソースを渡す
    domain_name=config_dev["api_gateway"]["domain_name"],
    certificate_arn=config_dev["api_gateway"]["certificate_arn"],
    auth_stack=auth_stack_dev,  # AuthStackインスタンスを直接渡す
    env=env,
)

# ApiStack (prod)
ApiStack(
    app,
    "SakeTrailApiProduction",
    bucket=ai_label_stack_prod.bucket,  # prod用S3バケットリソースを渡す
    domain_name=config_prod["api_gateway"]["domain_name"],
    certificate_arn=config_prod["api_gateway"]["certificate_arn"],
    auth_stack=auth_stack_prod,  # AuthStackインスタンスを直接渡す
    env=env,
)

app.synth() 