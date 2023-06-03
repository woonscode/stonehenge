import json
import boto3
import pandas as pd
from datetime import datetime

def handler(event, context):

    message = main()

    return {"message": message}

def main(file_dir="/tmp", file_name="full_poi_results"):

    # Initialise S3 client
    client = boto3.client("s3")

    object_keys = list_all_s3_objects(client)
    result_dict = {}

    # Open each JSON file and write to output dictionary
    for obj in object_keys:
        data = get_s3_object(client, "stonehenge-fyp", obj)

        for key, value in data.items():
            result_dict[key] = value

    # Write the records to a JSON file
    file_path = f"{file_dir}/{file_name}.json"

    with open(file_path, "w+") as output_file:
        json.dump(result_dict, output_file, indent=4)

    # Upload JSON file to S3
    upload_to_s3(client, file_path, f"{file_name}.json")

    # Convert JSON file to CSV and upload to S3
    convert_to_csv_and_upload(client, file_dir, file_name)

    return "Data merged, saved to file and uploaded to S3"

# List objects in bucket and save all keys to variable
def list_all_s3_objects(client):
    object_keys = []

    end_of_bucket = False
    token = ""
    # Get current date for object key prefix
    current_date = datetime.today().strftime('%Y-%m-%d')
    prefix = f"poi-api/{current_date}/google-maps/"

    # Retrieve objects from every page of S3 bucket
    while not end_of_bucket:
        if token == "":
            response = client.list_objects_v2(Bucket="stonehenge-fyp", Prefix=prefix, MaxKeys=1000)
        else:
            response = client.list_objects_v2(Bucket="stonehenge-fyp", Prefix=prefix, ContinuationToken=token, MaxKeys=1000)

        if response["Contents"]:
            for obj in response["Contents"]:
                object_keys.append(obj["Key"])

        if response["IsTruncated"]:
            token = response["NextContinuationToken"]
        else:
            end_of_bucket = True

    return object_keys

def get_s3_object(client, bucket, key):
    response = client.get_object(Bucket=bucket, Key=key)
    obj_data = response["Body"].read()

    return json.loads(obj_data)

# Upload file to S3 as an object
def upload_to_s3(client, file_path, object_name):

    # Get current date for object key prefix
    current_date = datetime.today().strftime('%Y-%m-%d')
    final_key = f"poi-api/{current_date}/{object_name}"

    with open(file_path, "rb") as f:
        client.upload_fileobj(f, "stonehenge-fyp", final_key)

def convert_to_csv_and_upload(client, file_dir, file_name):
    # Read the file as a df
    df = pd.read_json(f"{file_dir}/{file_name}.json", orient="index")

    # Reset the index and rename columns to be more human-readable
    df.reset_index(inplace=True, drop=True)
    df = df.rename(columns={"lat": "latitude", "lon": "longitude"})

    file_path = f"{file_dir}/{file_name}.csv"

    # Write the df to a csv
    df.to_csv(file_path)

    # Upload CSV file to S3
    upload_to_s3(client, file_path, f"{file_name}.csv")