output "poi_sqs_arn" {
  value       = aws_sqs_queue.poi_gmaps.arn
  description = "ARN of POI-GMaps SQS queue"
}

output "data_blender_sqs_arn" {
  value       = aws_sqs_queue.data_blender.arn
  description = "ARN of Data-Blender SQS queue"
}
