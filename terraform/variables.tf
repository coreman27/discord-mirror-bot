variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "The Google Cloud region"
  type        = string
  default     = "us-central1"
}

variable "github_owner" {
  description = "The GitHub repository owner"
  type        = string
}

variable "github_repo" {
  description = "The GitHub repository name"
  type        = string
}

variable "discord_token" {
  description = "The Discord Bot Token"
  type        = string
  sensitive   = true
}

variable "source_channel_id" {
  description = "The Source Channel ID"
  type        = string
}

variable "destination_channel_id" {
  description = "The Destination Channel ID"
  type        = string
}
