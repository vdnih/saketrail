import os
import json
import pytest
from lambdas.presign_url.presign_url import handler
from moto import mock_aws
import boto3

BUCKET_NAME = 'test-bucket'

@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv('BUCKET_NAME', BUCKET_NAME)

# 正常系: 正しいbodyが渡された場合、署名付きURLとjob_idが返ることを確認
@mock_aws
def test_presign_url_success():
    # S3バケット作成
    s3 = boto3.client('s3', region_name='ap-northeast-1')
    s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': 'ap-northeast-1'})

    event = {
        'body': json.dumps({'content_type': 'image/jpeg'})
    }
    result = handler(event, None)
    assert result['statusCode'] == 200
    body = json.loads(result['body'])
    assert 'upload_url' in body
    assert 'job_id' in body
    assert body['upload_url'].startswith('http')

# 異常系: bodyが不正なJSONの場合、400エラーとエラーメッセージが返ることを確認
@mock_aws
def test_presign_url_invalid_body():
    s3 = boto3.client('s3', region_name='ap-northeast-1')
    s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': 'ap-northeast-1'})

    event = {'body': 'not a json'}
    result = handler(event, None)
    assert result['statusCode'] == 400
    body = json.loads(result['body'])
    assert 'error' in body

# 異常系: bodyが存在しない場合、400エラーとエラーメッセージが返ることを確認
@mock_aws
def test_presign_url_missing_body():
    s3 = boto3.client('s3', region_name='ap-northeast-1')
    s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': 'ap-northeast-1'})

    event = {}  # bodyなし
    result = handler(event, None)
    assert result['statusCode'] == 400
    body = json.loads(result['body'])
    assert 'error' in body

# 異常系: 許可されていないMIMEタイプの場合、400エラーとエラーメッセージが返ることを確認
@mock_aws
def test_presign_url_invalid_mime_type():
    s3 = boto3.client('s3', region_name='ap-northeast-1')
    s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': 'ap-northeast-1'})

    event = {
        'body': json.dumps({'content_type': 'application/pdf'})
    }
    result = handler(event, None)
    assert result['statusCode'] == 400
    body = json.loads(result['body'])
    assert 'error' in body 