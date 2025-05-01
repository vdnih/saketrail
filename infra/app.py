#!/usr/bin/env python3
import os
import yaml
from aws_cdk import App, Environment
from saketrail_cdk.stacks.frontend_stack import FrontendStack
from saketrail_cdk.stacks.auth_stack import AuthStack

app = App()

def load_config(env_name):
    config_path = os.path.join(os.path.dirname(__file__), f'../config/{env_name}/frontend.yml')
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
AuthStack(
    app,
    "SakeTrailAuthDev",
    environment="dev",
    env=env,
)

# FrontendStack (dev)
FrontendStack(
    app,
    "SakeTrailFrontendDev",
    environment="dev",
    domain_name=config_dev["domain"],
    certificate_arn=config_dev["certificate_arn"],
    env=env,
)

# AuthStack (prod)
AuthStack(
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
    domain_name=config_prod["domain"],
    certificate_arn=config_prod["certificate_arn"],
    env=env,
)

app.synth() 