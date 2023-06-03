import re
import requests
import json
import boto3
import os
from requests.structures import CaseInsensitiveDict
from datetime import datetime
from urllib.parse import urlencode as encode

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
    messages = event["Records"]

    records = {}
    for message in messages:
        body = json.loads(message["body"])
        for key, value in body.items():
            records[key] = value

    message = main(records)

    return {"message": message}

def main(records, file_dir="/tmp"):
    # Retrieve Google Maps API Key from environment variables
    google_api_key = os.environ["GOOGLE_API_KEY"]

    s3_client = boto3.client("s3")

    record_dict = records
    file_name = ""

    # Make API request to Google Places (Place Search + Place Details)
    for id in record_dict.keys():
        record = record_dict[id]
        file_name += id
        try:
            term = record["name"]
            lon, lat = record["lon"], record["lat"]
            google_response = google_place_details(term, lon, lat, google_api_key)
            relavant_record = poi_schema_formatter(google_response["result"], poi_data_schema)
        except Exception as e:
            print(e)
            relavant_record = {}
        
        # Combine the results
        record_dict[id].update(relavant_record)
    
    hashed_file_name = hash(file_name)
    file_path = f"{file_dir}/{hashed_file_name}.json"
    # Write the response to a JSON file
    with open(file_path, 'w+') as file:
        json.dump(record_dict, file, indent=4)
    
    # Upload JSON file to S3
    upload_to_s3(s3_client, file_path, f"{hashed_file_name}.json")

    message = "Output generated and files uploaded to S3 bucket"

    return message

def upload_to_s3(client, file_path, object_name):

    # Get current date to store data under this key
    current_date = datetime.today().strftime('%Y-%m-%d')
    final_key = f"poi-api/{current_date}/google-maps/{object_name}"

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

def google_place_details(term, long, lat, google_api_key):
    """
    Function to make API request to Google Places (Place Search + Place Details)
    """
    # format placesearch url, use uri encoding

    query = {
        "query": term,
        "location": f"{lat},{long}",
        "key": google_api_key
    }

    query_term = encode(query)
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?{query_term}"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    google_response = requests.get(url, headers=headers)
    
    # get place_id from placesearch response
    place_id = google_response.json()["results"][0]["place_id"]
    
    # format placedetails url, use uri encoding
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,rating,formatted_phone_number,opening_hours,website,business_status,user_ratings_total,vicinity&key={google_api_key}"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    final_response = requests.get(url, headers=headers)
    return final_response.json()