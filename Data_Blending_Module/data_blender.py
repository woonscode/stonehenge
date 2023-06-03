import boto3
import pandas as pd
import numpy as np
import math
import json
from datetime import datetime

# Lambda Handling Function
def handler(event, context):
    messages = event["Records"]
    batch_record_ls = []

    for message in messages:
        body = json.loads(message["body"])
        batch_record_ls.append(body)

    message = main(batch_record_ls)

    return {"message": message}

def main(record_ls):
    # Initialise output
    output = []

    # Initialise S3 client
    client = boto3.client("s3")

    # Load POI DF
    download_s3_object(client, "stonehenge-fyp", "full_poi_results.csv")
    poi_df = pd.read_csv("/tmp/full_poi_results.csv")

    # Function configurations
    target_distance = [1,3,5] # in km
    to_aggregate = [
        'access',
        'amenity',
        'atm',
        'bakery',
        'bank',
        'beauty',
        'bus',
        'cafe',
        'casino',
        'childcare',
        'cinema',
        'cleaning',
        'clinic_or_praxis',
        'college',
        'convenience',
        'bar',
        'beach',
        'brothel',
        'dentist',
        'department_store',
        'dogs',
        'dog_park',
        'dry_cleaning',
        'education',
        'educational_institution',
        'entertainment',
        'financial',
        'food_and_drink',
        'food_court',
        'fuel',
        'garden',
        'gynaecology',
        'hairdresser',
        'health_and_beauty',
        'healthcare',
        'hospital',
        'kindergarten',
        'language_school',
        'laundry',
        'leisure',
        'library',
        'monorail',
        'music_school',
        'nightclub',
        'no_dogs',
        'park',
        'pet',
        'pharmacy',
        'playground',
        'police',
        'pub',
        'public_bath',
        'public_transport',
        'restaurant',
        'sand',
        'school',
        'service',
        'shopping_mall',
        'sport',
        'stationery',
        'subway',
        'super_market',
        'swimming_pool',
        'toy_and_game',
        'train',
        'tram',
        'transportation',
        'university',
        'vegan' ,
        'veterinary',
        'wheelchair'
    ]
    
    add_columns = ["total_count","average_rating","average_opening_hours"]
    
    # Iterate through the records
    for record in record_ls:
        lon = record['longitude']
        lat = record['latitude']

        # Generate the record
        record = generate_record(lon, lat, poi_df, to_aggregate,add_columns, target_distance)
        output.append(record)

    # Convert to dataframe and output to CSV
    output_df = pd.DataFrame(output)
    
    # Generate hashed name
    file_name = generate_file_name(record_ls)
    file_path = f"/tmp/{file_name}.csv"

    # Output to CSV
    output_df.to_csv(file_path, index=False)

    # Upload CSV file to S3
    upload_to_s3(client, file_path, f"{file_name}.csv")

    message = "Output generated and files uploaded to S3 bucket"

    return message

# Helper Functions
def getLandmarksWithinDistance(df, target_distance, lat, lon):
    """ 
    Get the landmarks within the target distance from the given dataframe
    Expected input: 
    - a dataframe with columns 'latitude' and 'longitude'
    - target_distance: the target distance in km
    - lat: latitude of the current location
    - lon: longitude of the current location
    Expected output: 
    - a dataframe with columns 'latitude' and 'longitude' and 'distance'
    """
    
    # Get the landmarks within the target distance
    df['distance'] = df.apply(lambda x: getDistanceFromLatLonInKm(lat, lon, x['latitude'], x['longitude']), axis=1)
    df = df[df['distance'] <= target_distance]
    return df
  
def get_category_ls(str_arr,cur_set=set()):
    """
    Get the list of categories from the string
    Expected input:
    - str_arr: the string of categories
    Expected output:
    - a list of categories
    """
    for i in str_arr.replace("[", "").replace("]", "").replace("'", "").replace(".", ",").replace(" ", "").split(","):
        cur_set.add(i)
    return cur_set

def getDistanceFromLatLonInKm(lat1,lon1,lat2,lon2):
    """ 
    Get the distance between 2 coordinates
    Expected input: 
    - lat1: latitude of the first coordinate
    - lon1: longitude of the first coordinate
    - lat2: latitude of the second coordinate
    - lon2: longitude of the second coordinate
    Expected output: 
    - the distance between the 2 coordinates in km
    """
    
    deg2rad = lambda x: x * (math.pi/180)
    R = 6371 # Radius of the earth in km
    dLat = deg2rad(lat2-lat1)  # deg2rad below
    dLon = deg2rad(lon2-lon1) 
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c # Distance in km
    return d
  
def categorical_aggregation(category,df):
    """
    Get the category string, filter out the points from the df and aggregate summary statistics.
    Expected input:
    - category: string
    - df: A pandas DataFrame containing values that meets the search radius criteria
    Expected output:
    - count: integer
    - average: rating
    """
    
    filtered_df = df[df.categories.apply(lambda x: category in x)]
    return filtered_df

def convert_to_24hr(string):
    """
    Convert a string in the format of "11:00 AM" to hours elapsed since midnight:
    Expected input: "11:00 AM"
    Expected output: 11
    """
    time = 0
    if string.split(":")[0] == "12":
        string = "0"+string[2:]
    if "PM" in string:
        time += int(string.split(":")[0]) + 12
    else:
        time += int(string.split(":")[0])
    
    return time+int(string.split(":")[1].split(" ")[0])/60
    
def get_total_operating_hours(string):
    """
    Get the total operating hours from a string:
    Expected input: "Monday: 11:00 AM – 8:00 PM,Tuesday: 11:00 AM – 8:00 PM,Wednesday: 11:00 AM – 8:00 PM,Thursday: 11:00 AM – 8:00 PM,Friday: 11:00 AM – 8:00 PM,Saturday: 11:00 AM – 8:00 PM,Sunday: 11:00 AM – 8:00 PM"
    Expected output: 63
    """
    # Initialize the total hours
    if string == np.nan or string == None or string == "" or not isinstance(string, str):
        return np.nan
        
    total_hours = 0
    string=string.replace(" ", " ").replace("–", "-").replace("\u202f"," ")
    
    # Split the string by comma
    weekdays = string.split(",")
    for day_str in weekdays:
        try:
            time_str = day_str.split(":",maxsplit=1)[1].strip()
            start_time = time_str.split("-")[0].strip()
            end_time = time_str.split("-")[1].strip()
            total_hours += convert_to_24hr(end_time) - convert_to_24hr(start_time)
        except:
            continue
    return total_hours

def generate_record(lon,lat,poi_df,to_aggregate,add_columns,target_distances=[1,3]):
  """
  Generate a record for the current listing
  Expected input:
  - lon: longitude of the current location
  - lat: latitude of the current location
  - poi_df: the dataframe containing the POI details
  - to_aggregate: the list of categories to aggregate
  - add_columns: the list of columns to add
  - target_distances: the target distance in km
  Expected output:
  - a dictionary containing the aggregated values for the current listing
  """
  
  record_dict = dict([(f"{dist}km_{cat}_{col}",math.nan) for cat in to_aggregate for col in add_columns for dist in target_distances])
  record_dict["latitude"] = lat
  record_dict["longitude"] = lon
  
  for dist in target_distances:
    # Get the landmarks within the target distance
    result_df = getLandmarksWithinDistance(poi_df, dist, lat, lon)
    
    relevant_categories = set()
    for i in range(len(result_df)):
        relevant_categories = get_category_ls(result_df.iloc[i]['categories'],relevant_categories)
    
    for cat in relevant_categories:
        if cat in to_aggregate:
            # Aggregate the summary statistics
            filtered_df = categorical_aggregation(cat,result_df)
            # Get the total count
            record_dict[f"{dist}km_{cat}_total_count"] = len(filtered_df)

            if len(filtered_df) == 0:
                continue
            # Get the average rating
            record_dict[f"{dist}km_{cat}_average_rating"] = filtered_df['rating'].mean()
            # Get the average open hours, ignore the NaN values
            record_dict[f"{dist}km_{cat}_average_opening_hours"] = filtered_df['opening_hours'].apply(lambda x: get_total_operating_hours(x)).mean(skipna=True)
            
            # # Get the nearest landmark
            nearest_landmark = filtered_df.query("distance == distance.min()")
            record_dict[f"distance_to_nearest_{cat}_poi"] = nearest_landmark.distance.values[0]
  return record_dict

def generate_file_name(records):
    name = ""
    for record in records:
        name += str(record["id"])
    
    hashed = hash(name)

    return hashed

def upload_to_s3(client, file_path, object_name):

    # Get current date to store data under this key
    current_date = datetime.today().strftime('%Y-%m-%d')
    final_key = f"blended/{current_date}/parts/{object_name}"

    with open(file_path, "rb") as f:
        client.upload_fileobj(f, "stonehenge-fyp", final_key)

def download_s3_object(client, bucket, file_name):
    current_date = datetime.today().strftime('%Y-%m-%d')
    object_key = f"poi-api/{current_date}/{file_name}"

    with open(f"/tmp/{file_name}", "wb") as file:
        client.download_fileobj(Bucket=bucket, Key=object_key, Fileobj=file)

    return "Successfully downloaded"