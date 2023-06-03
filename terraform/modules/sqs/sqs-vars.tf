variable "gmaps_queue_name" {
  description = "Queue to be sent to GMaps-API-Scraper function"
  type = string
  default = "POI-GMaps"
}

variable "data_blender_queue_name" {
  description = "Queue to be sent to Data-Blender Lambda function"
  type = string
  default = "Data-Blender"
}