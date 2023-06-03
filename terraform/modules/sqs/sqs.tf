resource "aws_sqs_queue" "poi_gmaps" {
  name                       = var.gmaps_queue_name
  visibility_timeout_seconds = 5400
  message_retention_seconds  = 86400
  receive_wait_time_seconds  = 20
}

resource "aws_sqs_queue" "data_blender" {
  name                       = var.data_blender_queue_name
  visibility_timeout_seconds = 5400
  message_retention_seconds  = 86400
  receive_wait_time_seconds  = 20
}