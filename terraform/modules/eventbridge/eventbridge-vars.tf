variable "schedule_group_name" {
  description = "Name of schedule group"
  type = string
  default = "stonehenge-schedule-group"
}

variable "geoapify_params_file" {
  description = "Name of JSON file to be passed in to EventBridge as parametersr for the Geoapify API scraper Lambda function"
  type = string
}

variable "geoapify_lambda_invoker_arn" {
  description = "ARN of Geoapify-Lambda-Invoker from Lambda Terraform module"
  type        = string
}

variable "poi_data_merger_arn" {
  description = "ARN of POI-Data-Merger from Lambda Terraform module"
  type        = string
}

variable "blended_data_merger_arn" {
  description = "ARN of Blended-Data-Merger from Lambda Terraform module"
  type        = string
}