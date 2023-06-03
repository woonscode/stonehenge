# Terraform
This directory contains all Terraform files required for setting up of the AWS infrastructure. As it utilises artifacts produced by GitHub Actions, it should be used through the GitHub Actions workflow.

### EventBridge Configuration
The EventBridge Scheduler for automatic invocation of the `Geoapify-Lambda-Invoker` Lambda function has been hardcoded to utilise configuration for the Tokyo, Japan region only as found in `./modules/eventbridge/geoapify-parameters/japan-config.json`. Modify the `japan-config.json` file accordingly to your needs for categories following its format. Additionally, other regions can be added as well in other `.json` files as long as the format is followed and the Terraform files modified accordingly to use the new config files.

### S3 Bucket Upload Event Trigger
The S3 bucket upload event triggers have been hardcoded to look for file names with specific suffixes or specific names entirely. This can be modified accordingly in the Terraform files.

### Batch Send from SQS Queue to Lambda
Take note that the batch send does not always follow the exact queue records configured. The number of records in a batch should hence be taken as a maximum rather than an exact. For example, if the batching window finishes before the maximum number of records to be sent to the Lambda function is attained, it will send the number of records it has collected at that point in time.

Additionally, as the SQS queue has been configured to be of a Standard type rather than FIFO type, it has the possibility of duplicate records that will be sent to Lambda. However, this does not have any effect on the resulting dataset.

### Lambda Layer
**Take note that the `Data-Blender` Lambda function uses a Lambda layer that is not recognised by AWS officially. You can upload your own layer containing the Python numpy package and use that instead.**

The Lambda layer by Klayers can be found [here](https://github.com/keithrozario/Klayers).

[<< Go back to Project Root](https://github.com/dagangstas/Stonehenge)