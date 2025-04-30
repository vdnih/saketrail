#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from saketrail_cdk.stacks.frontend_stack import FrontendStack

app = App()

# 環境変数から設定を読み込み
account = os.getenv('AWS_ACCOUNT_ID')
region = os.getenv('AWS_REGION', 'ap-northeast-1')
env_name = os.getenv('ENVIRONMENT', 'dev')

# 環境の設定
env = Environment(
    account=account,
    region=region
)

# フロントエンドスタックの作成
FrontendStack(
    app,
    f'SakeTrailFrontend{env_name.capitalize()}',
    env_name=env_name,
    env=env
)

app.synth() 