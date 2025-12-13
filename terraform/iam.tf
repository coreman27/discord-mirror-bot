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

# Grant Cloud Scheduler's default service account permission to invoke Cloud Run
resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  service  = "discord-mirror"
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.discord_bot.email}"
}

# Grant Cloud Build Service Account permission to manage Cloud Scheduler jobs
resource "google_project_iam_member" "cloudbuild_scheduler_admin" {
  project = var.project_id
  role    = "roles/cloudscheduler.admin"
  member  = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

# Grant Cloud Build Service Account permission to manage Cloud Tasks queues
resource "google_project_iam_member" "cloudbuild_tasks_admin" {
  project = var.project_id
  role    = "roles/cloudtasks.admin"
  member  = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

# Grant Cloud Build Service Account permission to use the Discord Bot service account
# (Required to attach the service account to the Scheduler Job)
resource "google_service_account_iam_member" "cloudbuild_sa_user" {
  service_account_id = google_service_account.discord_bot.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}
