locals {
  # File path to be modified according to needs or geographic location
  geoapify_params = file("${path.module}/geoapify-parameters/${var.geoapify_params_file}")
  geoapify_lambda_invoker_config = {
    FunctionName   = var.geoapify_lambda_invoker_arn
    InvocationType = "Event"
    Payload        = local.geoapify_params
  }
  geoapify_lambda_invoker_scheduled_eventbridge_input = jsonencode(local.geoapify_lambda_invoker_config)

  poi_data_merger_lambda_config = {
    FunctionName   = var.poi_data_merger_arn
    InvocationType = "Event"
  }
  poi_data_merger_eventbridge_input = jsonencode(local.poi_data_merger_lambda_config)

  blended_data_merger_lambda_config = {
    FunctionName   = var.blended_data_merger_arn
    InvocationType = "Event"
  }
  blended_data_merger_eventbridge_input = jsonencode(local.blended_data_merger_lambda_config)
}

resource "aws_iam_role" "eventbridge_monthly" {
  name               = "poi-eventbridge-monthly-schedule"
  assume_role_policy = file("${path.module}/policies/monthly-schedule-trust-policy.json")
}

resource "aws_iam_policy" "eventbridge_monthly" {
  name        = "poi-eventbridge-monthly-schedule"
  path        = "/"
  description = "IAM policy for POI monthly EventBridge schedule role"

  policy = file("${path.module}/policies/monthly-schedule-permissions.json")
}

resource "aws_iam_role_policy_attachment" "eventbridge_monthly" {
  role       = aws_iam_role.eventbridge_monthly.name
  policy_arn = aws_iam_policy.eventbridge_monthly.arn
}

resource "aws_scheduler_schedule_group" "main" {
  name = var.schedule_group_name
}

resource "aws_scheduler_schedule" "geoapify_monthly_trigger" {
  name        = "geoapify-monthly-lambda-trigger"
  description = "Triggers Geoapify-Lambda-Invoker Lambda function on the 1st of every month at 00:00 SGT"
  group_name  = aws_scheduler_schedule_group.main.name

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 0 1 * ? *)"
  schedule_expression_timezone = "Singapore"

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:lambda:invoke"
    role_arn = aws_iam_role.eventbridge_monthly.arn

    input = local.geoapify_lambda_invoker_scheduled_eventbridge_input
  }
}

resource "aws_scheduler_schedule" "poi_data_merger_monthly_trigger" {
  name        = "poi-data-merger-monthly-lambda-trigger"
  description = "Triggers POI-Data-Merger Lambda function on the 1st of every month at 03:00 SGT"
  group_name  = aws_scheduler_schedule_group.main.name

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 3 1 * ? *)"
  schedule_expression_timezone = "Singapore"

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:lambda:invoke"
    role_arn = aws_iam_role.eventbridge_monthly.arn

    input = local.poi_data_merger_eventbridge_input
  }
}

resource "aws_scheduler_schedule" "blended_data_merger_monthly_trigger" {
  name        = "blended-data-merger-monthly-lambda-trigger"
  description = "Triggers Blended-Data-Merger Lambda function on the 1st of every month at 06:00 SGT"
  group_name  = aws_scheduler_schedule_group.main.name

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 6 1 * ? *)"
  schedule_expression_timezone = "Singapore"

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:lambda:invoke"
    role_arn = aws_iam_role.eventbridge_monthly.arn

    input = local.blended_data_merger_eventbridge_input
  }
}