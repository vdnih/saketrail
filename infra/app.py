#!/usr/bin/env python3
import os
import yaml
from aws_cdk import App, Environment
from saketrail_cdk.stacks.frontend_stack import FrontendStack

app = App()

# 設定ファイルの読み込み
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/dev/frontend.yml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

config = load_config()

env = Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "ap-northeast-1")
)

FrontendStack(
    app,
    "SakeTrailFrontendDev",
    environment="dev",
    domain_name=config["domain"],
    certificate_arn=config["certificate_arn"],
    env=env,
)

app.synth() 