import re
import requests
import json
import os
from requests.structures import CaseInsensitiveDict
from dotenv import load_dotenv
from urllib.parse import urlencode as encode
import pandas as pd

# Load environment variables - ensure .env file is populated with Geoapify and Google Places API keys, refer to .env.example for more details
load_dotenv()

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
    categories = event["categories"]
    lon1 = event["lon1"]
    lat1 = event["lat1"]
    lon2 = event["lon2"]
    lat2 = event["lat2"]

    message = main(categories, lon1, lat1, lon2, lat2)

    return {"message": message}

def main(categories, lon1, lat1, lon2, lat2, file_dir='.', file_name='formatted-poi-details'):
    geoapify_limit_hit = False
    message = ""
    # Retrieve Geoapify API Keys from environment variables
    geoapify_api_key_list = os.environ["GEOAPIFY_API_KEYS"].split(",")
    geoapify_api_key_index = 0
    geoapify_api_key = geoapify_api_key_list[geoapify_api_key_index]

    # 98% free tier quota rotation
    geoapify_quota = 20 * 3000 * 0.98
    geoapify_record_count = 0

    geoapify_response_dict = dict()
    record_dict = dict()

    for category in categories:
        if geoapify_limit_hit:
            break

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
                    geoapify_record_count += 1

                    record = record["properties"]
                    id = record["place_id"]
                    formatted_record = poi_schema_formatter(record, poi_data_schema)
                    geoapify_response_dict[id] = formatted_record
                    record_dict[id] = formatted_record
                    
                page += 1

                # Rotate API keys to keep within free tier
                if geoapify_record_count >= geoapify_quota:
                    geoapify_api_key_index += 1

                    if geoapify_api_key_index >= len(geoapify_api_key_list):
                        geoapify_limit_hit = True
                        message += "Ran out of Geoapify API Keys! "
                        break

                    geoapify_api_key = geoapify_api_key_list[geoapify_api_key_index]
                    geoapify_record_count = 0

            except Exception as e:
                print(e)
                query_done = True
    # Write the records to a JSON file
    with open(f"{file_dir}/geoapify_response.json", 'w+') as file:
        json.dump(geoapify_response_dict, file, indent=4)

    # Retrieve Google Maps API Keys from environment variables
    google_api_key_list = os.environ["GOOGLE_API_KEYS"].split(",")
    google_api_key_index = 0
    google_api_key = google_api_key_list[google_api_key_index]

    # ~95% free tier quota rotation ($0.0875 per request, 200 free credits)
    google_quota = 2200
    google_record_count = 0

    # Function to make API request to Google Places (Place Search + Place Details)
    for id in record_dict.keys():
        record = record_dict[id]
        try:
            term = record["name"]
            lon, lat = record["lon"], record["lat"]
            google_record_count += 1
            google_response = google_place_details(term, lon, lat, google_api_key)
            relavant_record = poi_schema_formatter(google_response["result"], poi_data_schema)
        except Exception as e:
            print(e)
            relavant_record = {}
        
        # Combine the results
        record_dict[id].update(relavant_record)
        
        # Rotate API keys to keep within free tier
        if google_record_count >= google_quota:
            google_api_key_index += 1
            print("Rotating keys")

            if google_api_key_index >= len(google_api_key_list):
                message += "Ran out of Google Maps API Keys! "
                break 
            google_api_key = google_api_key_list[google_api_key_index]
            google_record_count = 0
    
    # Write the response to a JSON file
    with open(f"{file_dir}/{file_name}.json", 'w+') as file:
        json.dump(record_dict, file, indent=4)

    # Read the file as a df
    df = pd.read_json(f"{file_dir}/{file_name}.json", orient="index")
    # Reset the index
    df.reset_index(inplace=True, drop=True)
    df = df.rename(columns={"lat": "latitude", "lon": "longitude"})
    # write the df to a csv
    df.to_csv(f"{file_dir}/{file_name}.csv")

    message += "Output generated"

    return message
        
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

# Local Invocation
if __name__ == "__main__":
    categories = [
        "accommodation",
        "activity",
        "commercial",
        "catering",
        "education",
        "childcare",
        "entertainment",
        "healthcare",
        "heritage",
        "leisure",
        "man_made",
        "natural",
        "national_park",
        "office",
        "parking",
        "pet",
        "service",
        "tourism",
        "amenity",
        "beach",
        "adult",
        "airport",
        "sport",
        "public_transport",
        "production"
    ]

    # lon1, lat1, lon2, lat2 are coordinates corresponding to a box-sized shape that covers Tokyo
    event = {
        "categories": categories,
        "lon1": "138.951375",
        "lat1": "35.900432",
        "lon2": "139.940329",
        "lat2": "35.510811"
    }
    context = {}
    handler(event, context)