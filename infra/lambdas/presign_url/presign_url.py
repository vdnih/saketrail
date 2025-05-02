import os
import json
import uuid
import boto3

def handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    s3 = boto3.client('s3')

    # リクエストbodyのパース
    try:
        body = json.loads(event.get('body', '{}'))
        content_type = body.get('content_type')
        allowed_types = [
            'image/jpeg',
            'image/png',
            'image/webp',
            'image/gif',
        ]
        if not content_type:
            raise ValueError('content_type is required')
        if content_type not in allowed_types:
            raise ValueError(f'content_type {content_type} is not allowed')
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid request body: {e}'})
        }

    # job_id払い出し
    job_id = str(uuid.uuid4())
    key = f'uploads/{job_id}.jpg'

    # Presigned URL生成
    try:
        presigned_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ContentType': content_type,
            },
            ExpiresIn=600  # 10分
        )
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Failed to generate presigned url: {e}'})
        }

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'upload_url': presigned_url,
            'job_id': job_id
        })
    } 