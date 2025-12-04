# Get the default Cloud Compute Service Account (used by Cloud Run by default)
data "google_compute_default_service_account" "default" {}

# Grant Cloud Run Service Account access to secrets
resource "google_secret_manager_secret_iam_member" "run_access_token" {
  secret_id = google_secret_manager_secret.discord_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

resource "google_secret_manager_secret_iam_member" "run_access_source" {
  secret_id = google_secret_manager_secret.source_channel.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

resource "google_secret_manager_secret_iam_member" "run_access_dest" {
  secret_id = google_secret_manager_secret.dest_channel.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

# Grant Cloud Build Service Account access to secrets (to deploy)
data "google_project" "project" {}

resource "google_secret_manager_secret_iam_member" "build_access_token" {
  secret_id = google_secret_manager_secret.discord_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "build_access_source" {
  secret_id = google_secret_manager_secret.source_channel.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "build_access_dest" {
  secret_id = google_secret_manager_secret.dest_channel.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}
