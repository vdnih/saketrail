from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct
from typing import Optional


class FrontendStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        environment: str,
        domain_name: str,
        hosted_zone_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create subdomain based on environment
        subdomain = f"staging.{domain_name}" if environment == "staging" else domain_name

        # Import existing hosted zone
        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            "HostedZone",
            hosted_zone_id=hosted_zone_id,
            zone_name=domain_name,
        )

        # Create SSL certificate
        certificate = acm.DnsValidatedCertificate(
            self,
            "Certificate",
            domain_name=subdomain,
            hosted_zone=hosted_zone,
            region="us-east-1",  # CloudFront requires certificates in us-east-1
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

        # Create CloudFront distribution
        distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            domain_names=[subdomain],
            certificate=certificate,
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                )
            ],
        )

        # Create Route 53 alias record
        route53.ARecord(
            self,
            "AliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(distribution)
            ),
            record_name=subdomain,
        )

        # Output the distribution ID and bucket name
        CfnOutput(
            self,
            "DistributionId",
            value=distribution.distribution_id,
            description="CloudFront Distribution ID",
        )

        CfnOutput(
            self,
            "BucketName",
            value=website_bucket.bucket_name,
            description="Website Bucket Name",
        ) 