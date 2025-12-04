# Enable Secret Manager API
resource "google_project_service" "secretmanager" {
  service = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# Discord Token Secret
resource "google_secret_manager_secret" "discord_token" {
  secret_id = "discord-token"
  replication {
    automatic = true
  }
  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret_version" "discord_token" {
  secret = google_secret_manager_secret.discord_token.id
  secret_data = var.discord_token
}

# Source Channel ID Secret
resource "google_secret_manager_secret" "source_channel" {
  secret_id = "discord-source-channel"
  replication {
    automatic = true
  }
  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret_version" "source_channel" {
  secret = google_secret_manager_secret.source_channel.id
  secret_data = var.source_channel_id
}

# Destination Channel ID Secret
resource "google_secret_manager_secret" "dest_channel" {
  secret_id = "discord-dest-channel"
  replication {
    automatic = true
  }
  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret_version" "dest_channel" {
  secret = google_secret_manager_secret.dest_channel.id
  secret_data = var.destination_channel_id
}
