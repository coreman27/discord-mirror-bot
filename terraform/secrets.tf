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

# Source Channel ID Secret
resource "google_secret_manager_secret" "source_channel" {
  secret_id = "discord-source-channel"
  replication {
    automatic = true
  }
  depends_on = [google_project_service.secretmanager]
}

# Destination Channel ID Secret
resource "google_secret_manager_secret" "dest_channel" {
  secret_id = "discord-dest-channel"
  replication {
    automatic = true
  }
  depends_on = [google_project_service.secretmanager]
}

# Gemini API Key Secret (Container only - Value added manually)
resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  replication {
    automatic = true
  }
  depends_on = [google_project_service.secretmanager]
}
