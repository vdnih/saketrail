from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_s3_notifications as s3n,
    Duration,
    RemovalPolicy,
)
from constructs import Construct
import os
import yaml


def load_config(environment):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )
    # production → prod.yml へマッピング
    env_file = "prod.yml" if environment == "production" else f"{environment}.yml"
    config_path = os.path.join(base_dir, 'config', env_file)
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

class AiLabelRecognitionStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        environment: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        config = load_config(environment)
        ai_label_config = config["ai_label_recognition"]
        bucket_name = ai_label_config["s3_bucket"]
        table_name = ai_label_config["dynamodb_table"]

        # S3バケット（画像アップロード用）
        bucket = s3.Bucket(
            self,
            "AiLabelUploadBucket",
            bucket_name=bucket_name,
            removal_policy=RemovalPolicy.DESTROY if environment != 'production' else RemovalPolicy.RETAIN,
            auto_delete_objects=True if environment != 'production' else False,
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.PUT],
                    allowed_origins=["*"],
                    allowed_headers=["*"]
                )
            ]
        )
        self.bucket = bucket

        # DynamoDBテーブル（ジョブ管理）
        table = dynamodb.Table(
            self,
            "AiLabelJobTable",
            table_name=table_name,
            partition_key=dynamodb.Attribute(name="job_id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY if environment != 'production' else RemovalPolicy.RETAIN,
        )

        # Lambda関数（S3イベントで起動、AI認識処理のダミー）
        lambda_fn = _lambda.Function(
            self,
            "AiLabelRecognitionHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.main",
            code=_lambda.Code.from_asset(os.path.join("lambdas", "ai_label_recognition")),
            timeout=Duration.seconds(60),
            environment={
                "TABLE_NAME": table.table_name,
            },
        )
        bucket.grant_read(lambda_fn)
        table.grant_read_write_data(lambda_fn)

        # S3イベントでLambdaをトリガー
        notification = s3n.LambdaDestination(lambda_fn)
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, notification, s3.NotificationKeyFilter(prefix="uploads/")) 