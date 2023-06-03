import re
import requests
import json
import boto3
import os
from datetime import datetime
from requests.structures import CaseInsensitiveDict

# Schema for POI Data formatted
poi_data_schema = {
    "id": None,
    "name": None,
    "lon": None,
    "lat": None,
    "country": None,
    "city": None,
    "postcode": None,
    "suburb": None,
    "formatted": None,
    "categories": None,
    "rating": None,
    "user_ratings_total": None,
    "website": None,
    "opening_hours": None,
    "description": None,
    "business_status": None,
    "formatted_phone_number": None,
    "vicinity": None,
}

def handler(event, context):
    # Configure the search terms
    category = event["category"]
    lon1 = event["lon1"]
    lat1 = event["lat1"]
    lon2 = event["lon2"]
    lat2 = event["lat2"]

    message = main(category, lon1, lat1, lon2, lat2)

    return {"message": message}

def main(category, lon1, lat1, lon2, lat2, file_dir='/tmp'):
    # Retrieve Geoapify API Key from environment variables
    geoapify_api_key = os.environ["GEOAPIFY_API_KEY"]

    # Initialise S3 client for uploading
    client = boto3.client("s3")

    geoapify_response_dict = dict()
    record_dict = dict()

    # Iterate through to get all results
    page_size = 500
    page = 0
    
    query_done = False

    # Make API Request to get POIs by place id
    while not query_done:
        try:
            offset = page * page_size
            url = f"https://api.geoapify.com/v2/places?categories={category}&filter=rect:{lon1},{lat1},{lon2},{lat2}&limit={page_size}&offset={offset}&apiKey={geoapify_api_key}"
            
            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            poi_response = requests.get(url, headers=headers)
            
            if poi_response.json()["features"] == []:
                raise Exception("No more results found")
            
            for record in poi_response.json()["features"]:
                record = record["properties"]
                id = record["place_id"]
                formatted_record = poi_schema_formatter(record, poi_data_schema)
                geoapify_response_dict[id] = formatted_record
                record_dict[id] = formatted_record
                
            page += 1

        except Exception as e:
            print(e)
            query_done = True

    file_path = f"{file_dir}/{category}_geoapify_response.json"
    # Write the records to a JSON file
    with open(file_path, 'w+') as file:
        json.dump(geoapify_response_dict, file, indent=4)

    # Upload JSON file to S3
    upload_to_s3(client, file_path, f"{category}_geoapify_response.json")

    message = "Output generated and files uploaded to S3 bucket"

    return message

def upload_to_s3(client, file_path, object_name):

    # Get current date to store data under this key
    current_date = datetime.today().strftime('%Y-%m-%d')
    final_key = f"poi-api/{current_date}/geoapify/{object_name}"

    with open(file_path, "rb") as f:
        client.upload_fileobj(f, "stonehenge-fyp", final_key)
        
def poi_schema_formatter(input_dict, schema):
    """
    Formats the input dictionary to match the schema
    """
    output_dict = {}
    for key in schema:
        if key == "opening_hours":
            if "opening_hours" in input_dict:
                opening_hour_text = input_dict["opening_hours"]["weekday_text"]
                
                # Convert opening hours to a string
                opening_hour_text = ",".join(opening_hour_text)
                output_dict[key] = format_unicode_to_str(opening_hour_text)
                
        elif key in input_dict:
            if isinstance(input_dict[key], str):
                output_dict[key] = format_unicode_to_str(input_dict[key])
            else:
                output_dict[key] = input_dict[key]
    
    return output_dict    
    
def format_unicode_to_str(string):
    """This function will convert a string mixed with unicode and string to a string"""
    # Use regex to detect if there's unicode in the string
    if not re.match(r"\\u", string):
        return string
    
    output = ""
    for char in string:
        if re.match(r"\\u", char):
            # Convert unicode to string
            output += chr(int(char[2:]))
        else:
            output += char
    return output