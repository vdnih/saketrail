from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    aws_apigatewayv2_authorizers as authorizers,
    aws_iam as iam,
    aws_s3 as s3,
    aws_certificatemanager as acm,
    CfnOutput,
    aws_cognito as cognito,
)
from constructs import Construct
import os
import tempfile
from .auth_stack import AuthStack  # AuthStackをインポート

class ApiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucket: s3.Bucket,
        domain_name: str,
        certificate_arn: str,
        auth_stack: AuthStack,  # AuthStackを受け取る
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda関数（Presigned URL払い出し用）
        presign_lambda = _lambda.Function(
            self, 'PresignUrlLambda',
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler='presign_url.handler',
            code=_lambda.Code.from_asset(os.path.join('lambdas', 'presign_url')),
            environment={
                'BUCKET_NAME': bucket.bucket_name,
            },
        )
        bucket.grant_read_write(presign_lambda)

        # API Gatewayからのinvoke権限をLambdaに付与
        presign_lambda.add_permission(
            "ApiGatewayInvoke",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=f"arn:aws:execute-api:{self.region}:{self.account}:*/*/*/*"
        )

        # Lambda ARNをCloudFormation Outputとしてエクスポート
        CfnOutput(
            self,
            "PresignUrlLambdaArn",
            value=presign_lambda.function_arn,
            export_name=f"{self.stack_name}-PresignUrlLambdaArn"
        )

        # HTTP API (v2) 作成
        http_api = apigwv2.HttpApi(
            self, "SakeTrailHttpApi",
            api_name=f"SakeTrail HTTP API ({self.stack_name})",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_origins=["http://localhost:8080", "https://saketrail.vdnih.link"],
                allow_methods=[apigwv2.CorsHttpMethod.ANY],
                allow_headers=["Authorization", "Content-Type"],
            ),
            description="API for SakeTrail AI label recognition (HTTP API)",
        )

        # Cognito Authorizer
        cognito_authorizer = authorizers.HttpUserPoolAuthorizer(
            "CognitoAuthorizer",
            auth_stack.user_pool,
            authorizer_name="CognitoAuthorizer",
            identity_source=["$request.header.Authorization"],
            user_pool_clients=[auth_stack.user_pool_client],
        )

        # /ai/recognize-label/presigned-url POST
        http_api.add_routes(
            path="/ai/recognize-label/presigned-url",
            methods=[apigwv2.HttpMethod.POST],
            integration=integrations.HttpLambdaIntegration(
                "PresignUrlIntegration", presign_lambda
            ),
            authorizer=cognito_authorizer,
        )

        # 今後の拡張: /ai/recognize-label/{job_id} などもここに追加可能

        # ACM証明書を手動発行したARNで参照
        certificate = acm.Certificate.from_certificate_arn(
            self, "ApiCert", certificate_arn=certificate_arn
        )

        # カスタムドメイン設定
        custom_domain = apigwv2.DomainName(
            self, "CustomDomain",
            domain_name=domain_name,
            certificate=certificate,
        )
        apigwv2.ApiMapping(
            self, "BasePathMapping",
            api=http_api,
            domain_name=custom_domain,
            stage=http_api.default_stage,
        ) 