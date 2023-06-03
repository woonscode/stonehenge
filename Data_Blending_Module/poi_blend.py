import pandas as pd
import math
import json
import os
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
            # print("Aggregating for category: {}".format(cat))
            # Aggregate the summary statistics
            filtered_df = categorical_aggregation(cat,result_df)
            # Get the total count
            record_dict[f"{dist}km_{cat}_total_count"] = len(filtered_df)

            if len(filtered_df) == 0:
                continue
            # Get the average rating
            record_dict[f"{dist}km_{cat}_average_rating"] = filtered_df['rating'].mean()
            # Get the nearest landmark
            nearest_landmark = filtered_df.query("distance == distance.min()")
            record_dict[f"{dist}km_{cat}_nearest_name"] = nearest_landmark.name.values[0]
            record_dict[f"{dist}km_{cat}_nearest_rating"] = nearest_landmark.rating.values[0]
            record_dict[f"{dist}km_{cat}_nearest_rating_count"] = nearest_landmark.user_ratings_total.values[0]
            if not nearest_landmark.opening_hours.isnull().values.any():
                # print(nearest_landmark.opening_hours.values[0])
                record_dict[f"{dist}km_{cat}_nearest_opening_hours"] = get_total_operating_hours(nearest_landmark.opening_hours.values[0])
            
            if filtered_df['rating'].isnull().values.any():
                continue
            # Get the highest rated landmark
            highest_rating_landmark = filtered_df.query("rating == rating.max()")
            record_dict[f"{dist}km_{cat}_highest_name"] = highest_rating_landmark.name.values[0]
            record_dict[f"{dist}km_{cat}_highest_rating"] = highest_rating_landmark.rating.values[0]
            record_dict[f"{dist}km_{cat}_highest_rating_count"] = highest_rating_landmark.user_ratings_total.values[0]
            if not highest_rating_landmark.opening_hours.isnull().values.any():
                record_dict[f"{dist}km_{cat}_highest_opening_hours"] = get_total_operating_hours(highest_rating_landmark.opening_hours.values[0])
  return record_dict
  
def transform(poi_df,listing_df,to_aggregate,add_columns,target_distance, listing_file_name):
    """
    Transform the data
    Expected input:
    - poi_df: the dataframe containing the POI details
    - listing_df: the dataframe containing the listing details
    - to_aggregate: the list of categories to aggregate
    - add_columns: the list of columns to add
    - target_distance: the target distance in km
    - listing_file_name: the name of the listing file
    Expected output:
    - An output file containing the aggregated values for each listing in a csv format
    """
    
    output = []
    record_no = 0
    
    # Only iterate through the unique longitudes and latitudes
    building_df = listing_df.drop_duplicates(subset=["longitude","latitude"])
    
    # Iterate through the listings
    for i in range(len(building_df)):
        record_no +=1
        print("Processing record [{}]: {}/{}".format(listing_file_name,record_no,len(building_df)))
        # Get the current listing
        current_listing = listing_df.iloc[i]
        # Get the longitude and latitude
        lon = current_listing['longitude']
        lat = current_listing['latitude']

        # Generate the record
        record = generate_record(lon,lat,poi_df,to_aggregate,add_columns,target_distance)
        output.append(record)
        
    # Convert the output to a dataframe
    output_df = pd.DataFrame(output)
 
    # Combine such that new_df has the same number of rows as listing_df by matching the longitude and latitude
    new_df = pd.merge(listing_df,output_df.drop_duplicates(subset=["longitude","latitude"]),on=["longitude","latitude"],how="left")
    
    # Make sure the name,longitude and latitude are the first 3 columns
    cols = new_df.columns.tolist()
    # print(cols)
    df= new_df[['asset_name', 'longitude', 'latitude'] + [col for col in cols if col not in ['asset_name', 'longitude', 'latitude']]]
    
    # Save the output
    df.to_csv(f"./output/{listing_file_name}.csv",index=False)
  
def analyseCategories(df, min_occurences=1):
    """
    Given a dataframe, analyse the categories and return a dictionary containing the categories and their occurences
    Expected input:
    - df: the dataframe containing the POI details, must have a column named "categories" that is a list of categories
    - min_occurences: the minimum number of occurences for a category to be included in the output
    Expected output:
    - A dictionary containing the categories and their occurences
    """
    cat_set = dict()
    
    for i in range(len(df)):
        record_cat = str(df.iloc[i]["categories"])
        
        record_cat = record_cat.replace("[", "").replace("]", "").replace("'", "").replace(" ", "").replace(".",",").split(",")
        
        local_set = set(record_cat)
        for cat in local_set:
            if cat not in cat_set:
                cat_set[cat] = 1
            else:
                cat_set[cat] += 1
            
                    
    filtered_cat_set = dict()
    for key, value in cat_set.items():
        if key in ["nan","yes","no", ""]:
            continue
        if value >= min_occurences:
            filtered_cat_set[key] = value
    
    return dict(sorted(filtered_cat_set.items(), key=lambda x: x[1], reverse=True))
    
    
if __name__ == "__main__":
    
    # Get the file names and map
    mapping_input_files = {i.split("_cleaned")[0]:f"./input/listing/{i}" for i in os.listdir("./input/listing")}
    print(mapping_input_files)
    
    # Read the data
    poi_df = pd.read_csv("./input/poi/formatted-poi-details_updated.csv", low_memory=False)
    
    # To determine the categories to aggregate, you can use the function analyseCategories to get the categories and their occurences
    cat_counts = analyseCategories(poi_df, min_occurences=500)
    print(json.dumps(cat_counts, indent=4))
    
    # Function configurations
    target_distance = [1,3] # in km
    to_aggregate = ['public_transport','leisure','commercial','sport','office','healthcare','education','amenity','atm','convenience','pet','bank','shrine','hospital']
    
    add_columns = ["total_count","average_rating","nearest_name","nearest_rating","nearest_rating_count","nearest_opening_hours","highest_name","highest_rating","highest_rating_count","nearest_opening_hours"]
    
    # Iterate through the files and transform
    for file_name, file_path in mapping_input_files.items():
        # if file_name!= "test":
        #     continue
        # Read the listing data into a dataframe
        listing_df = pd.read_csv(file_path)
        # Transform the data
        transform(poi_df,listing_df,to_aggregate,add_columns,target_distance, file_name)
    
    