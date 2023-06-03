import boto3
import pandas as pd
import json

def handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    message = main(bucket)

    return {"message": message}

def main(bucket):
    # Initialise AWS service clients
    sqs_client = boto3.client("sqs")
    s3_client = boto3.client("s3")

    # List all listing data CSV files
    file_names = list_all_s3_objects(s3_client, bucket)

    # Get SQS Queue URL
    queue_url = sqs_client.get_queue_url(QueueName="Data-Blender")["QueueUrl"]

    # Download listing data from S3
    for file_name in file_names:
        download_s3_object(s3_client, bucket, file_name)

        df = pd.read_csv(f"/tmp/{file_name}")
        df = df.drop_duplicates(subset=['longitude','latitude'])

        df["source"] = file_name
        for index, record in df.iterrows():
            body = json.dumps(dict(record))
            # Publish each listing record to queue in separate messages
            sqs_client.send_message(QueueUrl=queue_url, MessageBody=body)

    return "Function finished"

def download_s3_object(client, bucket, file_name):
    object_key = f"listings/{file_name}"
    with open(f"/tmp/{file_name}", "wb") as file:
        client.download_fileobj(Bucket=bucket, Key=object_key, Fileobj=file)

    return "Successfully downloaded"

# List listing objects in bucket and save all keys to variable
def list_all_s3_objects(client, bucket):
    object_keys = []
    file_names = []

    end_of_bucket = False
    token = ""

    prefix = "listings/"

    # Retrieve objects from every page of S3 bucket
    while not end_of_bucket:
        if token == "":
            response = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1000)
        else:
            response = client.list_objects_v2(Bucket=bucket, Prefix=prefix, ContinuationToken=token, MaxKeys=1000)

        if response["Contents"]:
            for obj in response["Contents"]:
                object_keys.append(obj["Key"])

        if response["IsTruncated"]:
            token = response["NextContinuationToken"]
        else:
            end_of_bucket = True

    for key in object_keys:
        file_name = key.split("/")[-1]
        if file_name != "":
            file_names.append(file_name)

    return file_names