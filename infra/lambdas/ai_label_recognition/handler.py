import os
import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def main(event, context):
    # S3イベントからjob_idを抽出
    for record in event.get('Records', []):
        s3_key = record['s3']['object']['key']
        # 例: uploads/{job_id}.jpg
        if s3_key.startswith('uploads/') and s3_key.endswith('.jpg'):
            job_id = s3_key.split('/')[-1].replace('.jpg', '')
            # ダミーでDynamoDBにrunningを書き込む
            table.put_item(
                Item={
                    'job_id': job_id,
                    'status': 'running',
                    'type': None,
                    'result': None,
                    'created_at': record['eventTime'],
                    'updated_at': record['eventTime'],
                }
            )
    return {'statusCode': 200} 