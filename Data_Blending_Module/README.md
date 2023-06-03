# Data Blending Module

### Invocation
As the data pipeline is expected to be utilised only internally, the trigger endpoint has not been exposed to the public. There are 2 ways to trigger the data pipeline. 

The first is the automatic trigger at the 1st day of every month at 06:00 SGT (triggered by Amazon EventBridge Scheduler). This interval can be modified accordingly in the Terraform files to suit your needs.

The second way is to invoke the trigger Lambda function *(Blended-Data-Merger)* via the AWS SDK (boto3 for Python). No input arguments are needed. Take note that your AWS credentials must be configured beforehand.

### Intermediate Data
Intermediate data found in the `stonehenge-fyp` S3 bucket under the `blended/{specific_date}/parts` directory can be deleted as it has been merged to a singular file under `blended/{specific_date}/merged_parts.csv`. It has been left untouched for data archival purposes as of now.

[<< Go back to Project Root](https://github.com/dagangstas/Stonehenge)