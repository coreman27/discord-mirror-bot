# Create a dedicated Service Account for the Discord Bot
resource "google_service_account" "discord_bot" {
  account_id   = "discord-mirror-bot"
  display_name = "Discord Mirror Bot Service Account"
}

# Grant Cloud Run Service Account access to secrets
resource "google_secret_manager_secret_iam_member" "run_access_token" {
  secret_id = google_secret_manager_secret.discord_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.discord_bot.email}"
}

resource "google_secret_manager_secret_iam_member" "run_access_gemini" {
  secret_id = google_secret_manager_secret.gemini_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.discord_bot.email}"
}


# Grant Cloud Build Service Account access to secrets (to deploy)
data "google_project" "project" {}

resource "google_secret_manager_secret_iam_member" "build_access_token" {
  secret_id = google_secret_manager_secret.discord_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "build_access_gemini" {
  secret_id = google_secret_manager_secret.gemini_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}
