# API Scraping Module
The API Scraping Module's purpose is to obtain the data related to the Point of Interests (POIs) and its details found in a specified area. It utilises APIs from [Geoapify](https://apidocs.geoapify.com/) and [Google Maps](https://developers.google.com/maps/), extracting and merging only the relevant data from both APIs to obtain a more complete set of data.

We have 2 different versions of the module:
* `archived/poi_api_scraper.py` - Expected to be invoked locally on your machine, with entire module merged together in a single file and data outputted to a local directory *(Note: This file has an API key rotation capability to keep within free tiers of the various APIs*
* `./*.py` (rest of the files found in the current directory) - Module broken down into multiple different Lambda functions that are integrated together.

**For the project, we used the first version `archived/poi_api_scraper.py` to obtain our data due to cost concerns regarding API keys**

APIs used:
* [Geoapify Places API](https://apidocs.geoapify.com/docs/places/#about)
* Google Maps Places API
    * [Place Search](https://developers.google.com/maps/documentation/places/web-service/search-text)
    * [Place Details](https://developers.google.com/maps/documentation/places/web-service/details)

For greater customisation, a set of main relevant categories have been provided in both `archived/poi_api_scraper.py` and `geoapify_lambda_invoker.py`. Other input categories can be obtained from the following link: https://apidocs.geoapify.com/docs/places/#categories.

### Invocation
As the data pipeline is expected to be utilised only internally, the trigger endpoint has not been exposed to the public. There are 2 ways to trigger the data pipeline. 

The first is the automatic trigger at the 1st day of every month at 00:00 and 03:00 SGT (triggered by Amazon EventBridge Scheduler). This interval can be modified accordingly in the Terraform files to suit your needs.

The second way is to invoke the trigger Lambda function by navigating to the API_Scraping_Module directory and executing the following command: `python geoapify_lambda_invoker.py` with the input `categories` variable customised to your needs. Next, invoke the trigger Lambda function *(POI-Data-Merger)* via the AWS SDK (boto3 for Python). No input arguments are needed. Take note that your AWS credentials must be configured beforehand.

### Intermediate Data
Intermediate data found in the `stonehenge-fyp` S3 bucket under the `poi-api/{specific_date}/geoapify` and `poi-api/{specific_date}/google-maps` directory can be deleted as it has been merged to a singular file under `poi-api/{specific_date}/full_poi_results.csv`. It has been left untouched for data archival purposes as of now.

[<< Go back to Project Root](https://github.com/dagangstas/Stonehenge)
