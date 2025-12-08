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
