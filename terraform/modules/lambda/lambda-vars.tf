variable "geoapify_lambda_invoker_function_name" {
  description = "Name of Geoapify Lambda Invoker function"
  type = string
  default = "Geoapify-Lambda-Invoker"
}

variable "geoapify_api_scraper_function_name" {
  description = "Name of Geoapify POI API scraper Lambda function"
  type = string
  default = "Geoapify-API-Scraper"
}

variable "gmaps_lambda_queue_publisher_function_name" {
  description = "Name of Google Maps Lambda queue publisher Lambda function"
  type = string
  default = "GMaps-Lambda-Queue-Publisher"
}

variable "gmaps_api_scraper_function_name" {
  description = "Name of Google Maps API scraper Lambda function"
  type = string
  default = "GMaps-API-Scraper"
}

variable "poi_data_merger_function_name" {
  description = "Name of POI data merger Lambda function"
  type = string
  default = "POI-Data-Merger"
}

variable "data_blender_function_name" {
  description = "Name of data blender Lambda function"
  type = string
  default = "Data-Blender"
}

variable "data_blender_queue_publisher_function_name" {
  description = "Name of data blender queue publisher Lambda function"
  type = string
  default = "Data-Blender-Queue-Publisher"
}

variable "blended_data_merger_function_name" {
  description = "Name of blended data merger Lambda function"
  type = string
  default = "Blended-Data-Merger"
}

variable "GEOAPIFY_API_KEY" {
  description = "API Key for Geoapify"
  type = string
}

variable "GOOGLE_API_KEY" {
  description = "API Key for Google Maps"
  type = string
}

variable "source_bucket" {
  description = "Name of S3 bucket containing all data"
  type        = string
  default     = "stonehenge-fyp"
}

variable "poi_sqs_arn" {
  description = "ARN of POI-GMaps SQS queue from SQS Terraform module"
  type        = string
}

variable "data_blender_sqs_arn" {
  description = "ARN of Data-Blender SQS queue from SQS Terraform module"
  type        = string
}
