output "geoapify_lambda_invoker_arn" {
  value       = aws_lambda_function.geoapify_lambda_invoker.arn
  description = "ARN of Geoapify-Lambda-Invoker Lambda function"
}

output "poi_data_merger_arn" {
  value       = aws_lambda_function.poi_data_merger.arn
  description = "ARN of POI-Data-Merger Lambda function"
}

output "blended_data_merger_arn" {
  value       = aws_lambda_function.blended_data_merger.arn
  description = "ARN of Blended-Data-Merger Lambda function"
}