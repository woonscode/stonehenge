terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.51.0"
    }
  }
  backend "s3" {
    bucket     = "stonehenge-fyp"
    key        = "terraform/state"
    region     = "ap-southeast-1"
  }
}

# ENV variables for access_key and secret_key in pipeline
provider "aws" {
  region = "ap-southeast-1"
}

module "eventbridge" {
  source                           = "./modules/eventbridge"
  poi_data_merger_arn              = module.lambda.poi_data_merger_arn
  geoapify_lambda_invoker_arn      = module.lambda.geoapify_lambda_invoker_arn
  blended_data_merger_arn          = module.lambda.blended_data_merger_arn

  # Hardcoded to Japan config only, add on or modify as needed - config files can be added or modified in "./modules/eventbridge/geoapify-parameters" directory
  geoapify_params_file        = "japan-config.json"
}

module "sqs" {
  source = "./modules/sqs"
}

module "lambda" {
  source               = "./modules/lambda"
  GEOAPIFY_API_KEY     = var.GEOAPIFY_API_KEY
  GOOGLE_API_KEY       = var.GOOGLE_API_KEY
  poi_sqs_arn          = module.sqs.poi_sqs_arn
  data_blender_sqs_arn = module.sqs.data_blender_sqs_arn
}