import json
import boto3

# Make sure AWS Credentials are set - AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY
client = boto3.client("lambda")

# Categories obtained from the following link: https://apidocs.geoapify.com/docs/places/#categories

# # Categories we used, as of 2023-02-21
# categories = [
#     "accommodation",
#     "activity",
#     "commercial",
#     "catering",
#     "education",
#     "childcare",
#     "entertainment",
#     "healthcare",
#     "heritage",
#     "leisure",
#     "man_made",
#     "natural",
#     "national_park",
#     "office",
#     "parking",
#     "pet",
#     "service",
#     "tourism",
#     "amenity",
#     "beach",
#     "adult",
#     "airport",
#     "sport",
#     "public_transport",
#     "production"
# ]

def handler(event, context):
    message = ""
    categories = event["categories"]
    lon1 = event["lon1"]
    lat1 = event["lat1"]
    lon2 = event["lon2"]
    lat2 = event["lat2"]

    for category in categories:
        params = {
            "category": category,
            "lon1": lon1,
            "lat1": lat1,
            "lon2": lon2,
            "lat2": lat2
        }
        message += main(params)

    return {"message": message}

def main(params):

    # Data will be stored in S3 bucket - stonehenge-fyp
    response = client.invoke(
                FunctionName='Geoapify-API-Scraper',
                InvocationType='Event',
                LogType='None',
                Payload=json.dumps(params).encode("utf-8"),
            )
    
    status = response["StatusCode"]
    category = params["category"]

    # Return message on successful Lambda invocation
    if status == 202:
        result = f"Successfully invoked Geoapify Lambda function with {category} category \n"
        print(result)
        return result
    
    result = f"Failed to invoke Geoapify Lambda function with {category} category \n"
    print(result)
    return result

# Local Invocation
if __name__ == "__main__":

# Rectangle border of Tokyo used
# Top left corner of Tokyo border (longitude, latitude) - 138.951375, 35.900432
# Bottom right corner of Tokyo border (longitude, latitude) - 139.940329, 35.510811

    # Parameters
    categories = ["beach"]
    lon1 = "138.951375"
    lat1 = "35.900432"
    lon2 = "139.940329"
    lat2 = "35.510811"

    event = {
        "categories": categories,
        "lon1": lon1,
        "lat1": lat1,
        "lon2": lon2,
        "lat2": lat2
    }
    context = {}
    handler(event, context)