terraform {
  backend "gcs" {
    bucket  = "my-project-dev-479800-tfstate"
    prefix  = "discord-mirror"
  }
}
