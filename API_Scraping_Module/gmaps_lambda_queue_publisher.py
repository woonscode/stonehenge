import boto3
import json
import urllib.parse

def handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"], encoding="utf-8")
    message = main(bucket, key)

    return {"message": message}

def main(bucket, object_key):
    # Initialise AWS service clients
    sqs_client = boto3.client("sqs")
    s3_client = boto3.client("s3")

    # Get S3 object data
    data = get_s3_object(s3_client, bucket, object_key)

    # Get SQS Queue URL
    queue_url = sqs_client.get_queue_url(QueueName="POI-GMaps")["QueueUrl"]

    # Publish each Geoapify record to queue in separate messages
    for key, value in data.items():
        body = json.dumps({key: value})

        sqs_client.send_message(QueueUrl=queue_url, MessageBody=body)

def get_s3_object(client, bucket, object_key):
    response = client.get_object(Bucket=bucket, Key=object_key)
    obj_data = response["Body"].read()

    return json.loads(obj_data)