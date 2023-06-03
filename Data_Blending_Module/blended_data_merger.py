import boto3
import pandas as pd
from datetime import datetime

def handler(event, context):

    message = main()

    return {"message": message}

def main(bucket="stonehenge-fyp"):

    # Initialise merged_df
    merged_df = pd.DataFrame()

    # Initialise S3 client
    client = boto3.client("s3")

    # Get current date for object key prefix
    current_date = datetime.today().strftime("%Y-%m-%d")
    part_prefix = f"blended/{current_date}/parts/"

    # List all S3 object part CSV files
    part_file_keys = list_all_s3_objects(client, part_prefix)

    # Open each CSV file and write to output dataframe
    for part_file_key in part_file_keys:
        download_s3_object(client, bucket, part_file_key)
        part_file_name = part_file_key.split("/")[-1]
        df = pd.read_csv(f"/tmp/{part_file_name}")
        merged_df = pd.concat([merged_df, df])

    # Drop duplicates
    merged_df = merged_df.drop_duplicates(subset=["longitude","latitude"])

    # Upload merged file to S3
    merged_file_path = "/tmp/merged_parts.csv"
    merged_df.to_csv(merged_file_path)

    merged_file_key = f"blended/{current_date}/merged_parts.csv"
    upload_to_s3(client, merged_file_path, merged_file_key)

    # Download all listing data
    listing_prefix = "listings/"
    listing_file_keys = list_all_s3_objects(client, listing_prefix)

    # Load + left join data to original listing files
    for listing_file_key in listing_file_keys:
        listing_file_name = listing_file_key.split("/")[-1]

        if listing_file_name != "":
            download_s3_object(client, bucket, listing_file_key)
            listing_df = pd.read_csv(f"/tmp/{listing_file_name}")
            # Left join combined_df
            new_df = pd.merge(listing_df,merged_df, on=["longitude","latitude"], how="left")

            # Write the df to a CSV file
            output_file_path = f"/tmp/{listing_file_name}_blended.csv"
            new_df.to_csv(output_file_path)

            # Upload CSV file to S3
            final_key = f"blended/{current_date}/listings/{listing_file_name}_blended.csv"
            upload_to_s3(client, output_file_path, final_key)

    return "Data merged, saved to separate files and uploaded to S3"

def download_s3_object(client, bucket, object_key):
    file_name = object_key.split("/")[-1]
    with open(f"/tmp/{file_name}", "wb") as file:
        client.download_fileobj(Bucket=bucket, Key=object_key, Fileobj=file)

    return "Successfully downloaded"

# List objects in bucket and save all keys to variable
def list_all_s3_objects(client, prefix):
    object_keys = []

    end_of_bucket = False
    token = ""

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

# Upload file to S3 as an object
def upload_to_s3(client, file_path, object_key):

    with open(file_path, "rb") as f:
        client.upload_fileobj(f, "stonehenge-fyp", object_key)
