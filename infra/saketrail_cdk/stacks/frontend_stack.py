from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_certificatemanager as acm,
    RemovalPolicy,
    CfnOutput,
    aws_iam as iam,
)
from constructs import Construct
from typing import Optional
import yaml
import os


class FrontendStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        environment: str,
        domain_name: str,
        certificate_arn: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 開発環境(dev)の場合は何も作成しない
        if environment in ["dev", "development"]:
            return

        # Create subdomain based on environment
        subdomain = f"staging.{domain_name}" if environment == "staging" else domain_name

        # Create SSL certificate (DNS validation, manual CNAME)
        certificate = acm.Certificate.from_certificate_arn(
            self, "Certificate", certificate_arn
        )

        # Create S3 bucket for static website hosting
        website_bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            bucket_name=f"{environment}-saketrail-frontend",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        # OACの作成
        oac = cloudfront.CfnOriginAccessControl(
            self,
            "OAC",
            origin_access_control_config=cloudfront.CfnOriginAccessControl.OriginAccessControlConfigProperty(
                name=f"{construct_id}-oac",
                origin_access_control_origin_type="s3",
                signing_behavior="always",
                signing_protocol="sigv4",
                description="OAC for CloudFront to access S3"
            )
        )

        # CloudFront Distribution
        distribution = cloudfront.CfnDistribution(
            self,
            "Distribution",
            distribution_config=cloudfront.CfnDistribution.DistributionConfigProperty(
                enabled=True,
                default_root_object="index.html",
                aliases=[subdomain],
                viewer_certificate=cloudfront.CfnDistribution.ViewerCertificateProperty(
                    acm_certificate_arn=certificate_arn,
                    ssl_support_method="sni-only"
                ),
                origins=[
                    cloudfront.CfnDistribution.OriginProperty(
                        domain_name=website_bucket.bucket_regional_domain_name,
                        id="S3Origin",
                        s3_origin_config=cloudfront.CfnDistribution.S3OriginConfigProperty(
                            origin_access_identity=""
                        ),
                        origin_access_control_id=oac.ref,
                    )
                ],
                default_cache_behavior=cloudfront.CfnDistribution.DefaultCacheBehaviorProperty(
                    target_origin_id="S3Origin",
                    viewer_protocol_policy="redirect-to-https",
                    allowed_methods=["GET", "HEAD", "OPTIONS"],
                    cached_methods=["GET", "HEAD"],
                    compress=True,
                    cache_policy_id=cloudfront.CachePolicy.CACHING_OPTIMIZED.cache_policy_id,
                ),
                custom_error_responses=[
                    cloudfront.CfnDistribution.CustomErrorResponseProperty(
                        error_code=404,
                        response_code=200,
                        response_page_path="/index.html"
                    )
                ]
            )
        )

        # S3バケットポリシーにOACからのアクセスのみ許可
        website_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
                actions=["s3:GetObject"],
                resources=[f"{website_bucket.bucket_arn}/*"],
                conditions={
                    "StringEquals": {
                        "AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:distribution/{distribution.ref}"
                    }
                }
            )
        )

        # Output the distribution ID, domain name, bucket name, and ACM validation info
        CfnOutput(
            self,
            "DistributionId",
            value=distribution.ref,
            description="CloudFront Distribution ID",
        )

        CfnOutput(
            self,
            "BucketName",
            value=website_bucket.bucket_name,
            description="Website Bucket Name",
        )

def load_config(environment):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if environment == 'production':
        env_name = 'prod'
    else:
        env_name = environment
    config_path = os.path.join(base_dir, 'config', f'{env_name}.yml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config 