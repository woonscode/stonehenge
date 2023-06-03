## Geoapify Lambda Invoker
resource "aws_iam_role" "geoapify_lambda_invoker" {
  name               = "geoapify-lambda-invoker"
  assume_role_policy = file("${path.module}/policies/main-lambda-trust-policy.json")
}

resource "aws_cloudwatch_log_group" "geoapify_lambda_invoker" {
  name              = "/aws/lambda/${var.geoapify_lambda_invoker_function_name}"
  retention_in_days = 30
}

resource "aws_iam_policy" "geoapify_lambda_invoker" {
  name        = "geoapify-lambda-invoker"
  path        = "/"
  description = "IAM policy for Geoapify Lambda Invoker function"

  policy = file("${path.module}/policies/geoapify-lambda-invoker-permissions.json")
}

resource "aws_iam_role_policy_attachment" "geoapify_lambda_invoker" {
  role       = aws_iam_role.geoapify_lambda_invoker.name
  policy_arn = aws_iam_policy.geoapify_lambda_invoker.arn
}

resource "aws_lambda_function" "geoapify_lambda_invoker" {
  function_name = var.geoapify_lambda_invoker_function_name
  role          = aws_iam_role.geoapify_lambda_invoker.arn
  filename      = "${path.module}/../../../API_Scraping_Module/geoapify_lambda_invoker.zip"
  description   = "This function takes in a list of categories and invokes the Geoapify API Scraper Lambda function for each category."
  handler       = "geoapify_lambda_invoker.handler"
  runtime       = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/../../../API_Scraping_Module/geoapify_lambda_invoker.py")
  timeout       = 900

  depends_on = [
    aws_iam_role_policy_attachment.geoapify_lambda_invoker,
    aws_cloudwatch_log_group.geoapify_lambda_invoker,
  ]
}

## Geoapify API Scraper
resource "aws_iam_role" "geoapify_api_scraper" {
  name               = "geoapify-api-scraper"
  assume_role_policy = file("${path.module}/policies/main-lambda-trust-policy.json")
}

resource "aws_cloudwatch_log_group" "geoapify_api_scraper" {
  name              = "/aws/lambda/${var.geoapify_api_scraper_function_name}"
  retention_in_days = 30
}

resource "aws_iam_policy" "geoapify_api_scraper" {
  name        = "geoapify-api-scraper"
  path        = "/"
  description = "IAM policy for Geoapify API scraper Lambda function"

  policy = file("${path.module}/policies/geoapify-api-scraper-permissions.json")
}

resource "aws_iam_role_policy_attachment" "geoapify_api_scraper" {
  role       = aws_iam_role.geoapify_api_scraper.name
  policy_arn = aws_iam_policy.geoapify_api_scraper.arn
}

resource "aws_lambda_function" "geoapify_api_scraper" {
  function_name    = var.geoapify_api_scraper_function_name
  role             = aws_iam_role.geoapify_api_scraper.arn
  filename         = "${path.module}/../../../API_Scraping_Module/geoapify_api_scraper.zip"
  description      = "This function returns all the points of interests and their specific data according to the input category and location, obtained from Geoapify APIs."
  handler          = "geoapify_api_scraper.handler"
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../../API_Scraping_Module/geoapify_api_scraper.py")
  timeout          = 900
  memory_size      = 1024

  # Name of environment variables to be passed to Lambda function, obtained from pipeline
  environment {
    variables = {
      "GEOAPIFY_API_KEY" = var.GEOAPIFY_API_KEY
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.geoapify_api_scraper,
    aws_cloudwatch_log_group.geoapify_api_scraper,
  ]
}

## GMaps Lambda Queue Publisher
resource "aws_iam_role" "gmaps_lambda_queue_publisher" {
  name               = "gmaps-lambda-queue-publisher"
  assume_role_policy = file("${path.module}/policies/main-lambda-trust-policy.json")
}

resource "aws_cloudwatch_log_group" "gmaps_lambda_queue_publisher" {
  name              = "/aws/lambda/${var.gmaps_lambda_queue_publisher_function_name}"
  retention_in_days = 30
}

resource "aws_iam_policy" "gmaps_lambda_queue_publisher" {
  name        = "gmaps-lambda-queue-publisher"
  path        = "/"
  description = "IAM policy for Google Maps queue publisher Lambda function"

  policy = file("${path.module}/policies/gmaps-lambda-queue-publisher-permissions.json")
}

resource "aws_iam_role_policy_attachment" "gmaps_lambda_queue_publisher" {
  role       = aws_iam_role.gmaps_lambda_queue_publisher.name
  policy_arn = aws_iam_policy.gmaps_lambda_queue_publisher.arn
}

resource "aws_lambda_function" "gmaps_lambda_queue_publisher" {
  function_name    = var.gmaps_lambda_queue_publisher_function_name
  role             = aws_iam_role.gmaps_lambda_queue_publisher.arn
  filename         = "${path.module}/../../../API_Scraping_Module/gmaps_lambda_queue_publisher.zip"
  description      = "This function is triggered on each object uploaded to the stonehenge-fyp bucket, reading the object and publishing to an SQS queue for each record in the object."
  handler          = "gmaps_lambda_queue_publisher.handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/../../../API_Scraping_Module/gmaps_lambda_queue_publisher.py")
  timeout          = 900

  depends_on = [
    aws_iam_role_policy_attachment.gmaps_lambda_queue_publisher,
    aws_cloudwatch_log_group.gmaps_lambda_queue_publisher,
  ]
}

resource "aws_lambda_permission" "s3_permission_to_trigger_gmaps_queue_publisher_lambda" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.gmaps_lambda_queue_publisher.arn
  principal     = "s3.amazonaws.com"
  statement_id  = "AllowGMapsLambdaQueuePublisherExecutionFromS3Bucket"
}

## GMaps API Scraper
resource "aws_iam_role" "gmaps_api_scraper" {
  name               = "gmaps-api-scraper"
  assume_role_policy = file("${path.module}/policies/main-lambda-trust-policy.json")
}

resource "aws_cloudwatch_log_group" "gmaps_api_scraper" {
  name              = "/aws/lambda/${var.gmaps_api_scraper_function_name}"
  retention_in_days = 30
}

resource "aws_iam_policy" "gmaps_api_scraper" {
  name        = "gmaps-api-scraper"
  path        = "/"
  description = "IAM policy for Google Maps API scraper Lambda function"

  policy = file("${path.module}/policies/gmaps-api-scraper-permissions.json")
}

resource "aws_iam_role_policy_attachment" "gmaps_api_scraper" {
  role       = aws_iam_role.gmaps_api_scraper.name
  policy_arn = aws_iam_policy.gmaps_api_scraper.arn
}

resource "aws_lambda_function" "gmaps_api_scraper" {
  function_name    = var.gmaps_api_scraper_function_name
  role             = aws_iam_role.gmaps_api_scraper.arn
  filename         = "${path.module}/../../../API_Scraping_Module/gmaps_api_scraper.zip"
  description      = "This function takes in a batch of records from an SQS queue and calls the Google Maps Places API for each record."
  handler          = "gmaps_api_scraper.handler"
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("${path.module}/../../../API_Scraping_Module/gmaps_api_scraper.py")
  timeout          = 900

  # Name of environment variables to be passed to Lambda function, obtained from pipeline
  environment {
    variables = {
      "GOOGLE_API_KEY" = var.GOOGLE_API_KEY
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.gmaps_api_scraper,
    aws_cloudwatch_log_group.gmaps_api_scraper,
  ]
}

resource "aws_lambda_event_source_mapping" "poi_sqs_trigger" {
  batch_size                         = 50
  event_source_arn                   = var.poi_sqs_arn
  function_name                      = aws_lambda_function.gmaps_api_scraper.arn
  maximum_batching_window_in_seconds = 120
}

## POI Data Merger
resource "aws_iam_role" "poi_data_merger" {
  name               = "poi-data-merger"
  assume_role_policy = file("${path.module}/policies/main-lambda-trust-policy.json")
}

resource "aws_cloudwatch_log_group" "poi_data_merger" {
  name              = "/aws/lambda/${var.poi_data_merger_function_name}"
  retention_in_days = 30
}

resource "aws_iam_policy" "poi_data_merger" {
  name        = "poi-data-merger"
  path        = "/"
  description = "IAM policy for POI data merger Lambda function"

  policy = file("${path.module}/policies/data-merger-permissions.json")
}

resource "aws_iam_role_policy_attachment" "poi_data_merger" {
  role       = aws_iam_role.poi_data_merger.name
  policy_arn = aws_iam_policy.poi_data_merger.arn
}

resource "aws_lambda_function" "poi_data_merger" {
  function_name    = var.poi_data_merger_function_name
  role             = aws_iam_role.poi_data_merger.arn
  filename         = "${path.module}/../../../API_Scraping_Module/poi_data_merger.zip"
  description      = "This function gets all objects from a given bucket and key and merges all of them together into a single file."
  handler          = "poi_data_merger.handler"
  layers           = ["arn:aws:lambda:ap-southeast-1:336392948345:layer:AWSSDKPandas-Python39:5"]
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/../../../API_Scraping_Module/poi_data_merger.py") 
  timeout          = 900
  memory_size      = 1024

  depends_on = [
    aws_iam_role_policy_attachment.poi_data_merger,
    aws_cloudwatch_log_group.poi_data_merger,
  ]
}

## Data Blender Queue Publisher
resource "aws_iam_role" "data_blender_queue_publisher" {
  name               = "data-blender-queue-publisher"
  assume_role_policy = file("${path.module}/policies/main-lambda-trust-policy.json")
}

resource "aws_cloudwatch_log_group" "data_blender_queue_publisher" {
  name              = "/aws/lambda/${var.data_blender_queue_publisher_function_name}"
  retention_in_days = 30
}

resource "aws_iam_policy" "data_blender_queue_publisher" {
  name        = "data-blender-queue-publisher"
  path        = "/"
  description = "IAM policy for data blender queue publisher Lambda function"

  policy = file("${path.module}/policies/data-blender-queue-publisher-permissions.json")
}

resource "aws_iam_role_policy_attachment" "data_blender_queue_publisher" {
  role       = aws_iam_role.data_blender_queue_publisher.name
  policy_arn = aws_iam_policy.data_blender_queue_publisher.arn
}

resource "aws_lambda_function" "data_blender_queue_publisher" {
  function_name    = var.data_blender_queue_publisher_function_name
  role             = aws_iam_role.data_blender_queue_publisher.arn
  filename         = "${path.module}/../../../Data_Blending_Module/data_blender_queue_publisher.zip"
  description      = "This function is triggered on the final aggregated Geoapify output object uploaded to the stonehenge-fyp bucket. It reads listing data from the corresponding S3 objects and publish each record to an SQS queue."
  handler          = "data_blender_queue_publisher.handler"
  layers           = ["arn:aws:lambda:ap-southeast-1:336392948345:layer:AWSSDKPandas-Python39:5"]
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/../../../Data_Blending_Module/data_blender_queue_publisher.py")
  timeout          = 900
  memory_size      = 1024

  depends_on = [
    aws_iam_role_policy_attachment.data_blender_queue_publisher,
    aws_cloudwatch_log_group.data_blender_queue_publisher,
  ]
}

resource "aws_lambda_permission" "s3_permission_to_trigger_data_blender_lambda" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_blender_queue_publisher.arn
  principal     = "s3.amazonaws.com"
  statement_id  = "AllowDataBlenderLambdaExecutionFromS3Bucket"
}

resource "aws_s3_bucket_notification" "object_created" {
  bucket = var.source_bucket

  lambda_function {
    lambda_function_arn = aws_lambda_function.gmaps_lambda_queue_publisher.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "poi-api/"
    filter_suffix       = "_geoapify_response.json"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.data_blender_queue_publisher.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "poi-api/"
    filter_suffix       = "full_poi_results.csv"
  }

  depends_on = [
    aws_lambda_permission.s3_permission_to_trigger_gmaps_queue_publisher_lambda,
    aws_lambda_permission.s3_permission_to_trigger_data_blender_lambda,
  ]
}

## Data Blender
resource "aws_iam_role" "data_blender" {
  name               = "data-blender"
  assume_role_policy = file("${path.module}/policies/main-lambda-trust-policy.json")
}

resource "aws_cloudwatch_log_group" "data_blender" {
  name              = "/aws/lambda/${var.data_blender_function_name}"
  retention_in_days = 30
}

resource "aws_iam_policy" "data_blender" {
  name        = "data-blender"
  path        = "/"
  description = "IAM policy for data blender Lambda function"

  policy = file("${path.module}/policies/data-blender-permissions.json")
}

resource "aws_iam_role_policy_attachment" "data_blender" {
  role       = aws_iam_role.data_blender.name
  policy_arn = aws_iam_policy.data_blender.arn
}

resource "aws_lambda_function" "data_blender" {
  function_name    = var.data_blender_function_name
  role             = aws_iam_role.data_blender.arn
  filename         = "${path.module}/../../../Data_Blending_Module/data_blender.zip"
  description      = "This function takes in a batch of records from an SQS queue and blends the merged POI data with each record."
  handler          = "data_blender.handler"
  layers           = [
    "arn:aws:lambda:ap-southeast-1:336392948345:layer:AWSSDKPandas-Python39:5",
    "arn:aws:lambda:ap-southeast-1:770693421928:layer:Klayers-p39-numpy:11"
  ]
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/../../../Data_Blending_Module/data_blender.py")
  timeout          = 900
  memory_size      = 1024

  depends_on = [
    aws_iam_role_policy_attachment.data_blender,
    aws_cloudwatch_log_group.data_blender,
  ]
}

resource "aws_lambda_event_source_mapping" "data_blender_sqs_trigger" {
  batch_size                         = 50
  event_source_arn                   = var.data_blender_sqs_arn
  function_name                      = aws_lambda_function.data_blender.arn
  maximum_batching_window_in_seconds = 120
}

## Blended Data Merger
resource "aws_iam_role" "blended_data_merger" {
  name               = "blended-data-merger"
  assume_role_policy = file("${path.module}/policies/main-lambda-trust-policy.json")
}

resource "aws_cloudwatch_log_group" "blended_data_merger" {
  name              = "/aws/lambda/${var.blended_data_merger_function_name}"
  retention_in_days = 30
}

resource "aws_iam_policy" "blended_data_merger" {
  name        = "blended-data-merger"
  path        = "/"
  description = "IAM policy for blended data merger Lambda function"

  policy = file("${path.module}/policies/data-merger-permissions.json")
}

resource "aws_iam_role_policy_attachment" "blended_data_merger" {
  role       = aws_iam_role.blended_data_merger.name
  policy_arn = aws_iam_policy.blended_data_merger.arn
}

resource "aws_lambda_function" "blended_data_merger" {
  function_name    = var.blended_data_merger_function_name
  role             = aws_iam_role.blended_data_merger.arn
  filename         = "${path.module}/../../../Data_Blending_Module/blended_data_merger.zip"
  description      = "This function gets all objects from a given bucket and key and merges all of them together into a single file."
  handler          = "blended_data_merger.handler"
  layers           = ["arn:aws:lambda:ap-southeast-1:336392948345:layer:AWSSDKPandas-Python39:5"]
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("${path.module}/../../../Data_Blending_Module/blended_data_merger.py") 
  timeout          = 900
  memory_size      = 1024

  depends_on = [
    aws_iam_role_policy_attachment.blended_data_merger,
    aws_cloudwatch_log_group.blended_data_merger,
  ]
}