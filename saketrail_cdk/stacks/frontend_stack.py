from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3_deployment as s3deploy,
    RemovalPolicy,
    CfnOutput,
    Tags,
)
from constructs import Construct
import yaml
import os
from typing import Dict

class FrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 設定ファイルの読み込み
        self.config = self._load_config(env_name)
        
        # 共通タグの適用
        for key, value in self.config['common']['tags'].items():
            Tags.of(self).add(key, value)

        # S3バケットの作成
        website_bucket = s3.Bucket(
            self, 'WebsiteBucket',
            bucket_name=self.config['infra']['s3']['frontend_bucket']['name'],
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        # SSL証明書の作成
        certificate = acm.Certificate(
            self, 'Certificate',
            domain_name=self.config['common']['domain'],
            validation=acm.CertificateValidation.from_dns()
        )

        # CloudFront OriginAccessIdentityの作成
        origin_identity = cloudfront.OriginAccessIdentity(
            self, 'OriginAccessIdentity',
            comment=f'Access identity for {self.config["common"]["domain"]}'
        )

        # CloudFront Distributionの作成
        distribution = cloudfront.Distribution(
            self, 'Distribution',
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    website_bucket,
                    origin_access_identity=origin_identity
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            domain_names=[self.config['common']['domain']],
            certificate=certificate,
            default_root_object='index.html',
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path='/index.html'
                )
            ],
            price_class=getattr(
                cloudfront.PriceClass,
                self.config['infra']['cloudfront']['price_class']
            ),
            minimum_protocol_version=getattr(
                cloudfront.SecurityPolicyProtocol,
                self.config['infra']['cloudfront']['minimum_protocol_version']
            ),
        )

        # Route 53 レコードの作成
        hosted_zone = route53.HostedZone.from_lookup(
            self, 'HostedZone',
            domain_name='saketrail.com'
        )

        route53.ARecord(
            self, 'AliasRecord',
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(distribution)
            ),
            record_name=self.config['common']['domain']
        )

        # S3バケットポリシーの設定
        website_bucket.add_to_resource_policy(
            s3.PolicyStatement(
                actions=['s3:GetObject'],
                resources=[website_bucket.arn_for_objects('*')],
                principals=[origin_identity.grant_principal]
            )
        )

        # 出力
        CfnOutput(
            self, 'DistributionId',
            description='CloudFront Distribution ID',
            value=distribution.distribution_id
        )

        CfnOutput(
            self, 'BucketName',
            description='Website Bucket Name',
            value=website_bucket.bucket_name
        )

    def _load_config(self, env_name: str) -> Dict:
        """
        共通設定とインフラ設定を読み込んで結合します
        """
        # 共通設定の読み込み
        common_config_path = os.path.join('config', 'common', f'{env_name}.yml')
        with open(common_config_path, 'r') as f:
            common_config = yaml.safe_load(f)

        # インフラ設定の読み込み
        infra_config_path = os.path.join('infra', 'config', env_name, 'frontend.yml')
        with open(infra_config_path, 'r') as f:
            infra_config = yaml.safe_load(f)

        return {
            'common': common_config,
            'infra': infra_config
        } 