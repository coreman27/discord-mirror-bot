resource "google_cloudbuild_trigger" "discord_mirror_trigger" {
  name        = "discord-mirror-trigger"
  description = "Trigger for Discord Mirror Bot"

  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
      branch = "^main$"
    }
  }

  filename = "cloudbuild.yaml"
}
