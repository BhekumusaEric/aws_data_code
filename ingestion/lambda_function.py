import json
import boto3
import os
import base64

s3 = boto3.client('s3')
BUCKET = os.environ.get('BUCKET_NAME', 'your-s3-bucket-name')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        student_id = body.get('student_id')
        scores = json.dumps(body)

        key = f"students/student_{student_id}.json"
        s3.put_object(Bucket=BUCKET, Key=key, Body=scores)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Student data stored successfully.'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
