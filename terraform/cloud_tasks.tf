# Cloud Task Queue for scheduled tasks
resource "google_cloud_tasks_queue" "discord_bot_queue" {
  name     = "discord-bot-tasks"
  location = var.region
  
  rate_limits {
    max_dispatches_per_second = 1
    max_concurrent_dispatches = 1
  }

  retry_config {
    max_attempts       = 5
    max_retries        = 3
    max_backoff        = "3600s"
    min_backoff        = "10s"
    max_doublings      = 5
  }
}

# Cloud Scheduler Job for daily Wordle (5:00 AM Central = 10:00 AM UTC)
resource "google_cloud_scheduler_job" "daily_wordle" {
  name            = "discord-bot-daily-wordle"
  description     = "Trigger daily Wordle solving at 5:00 AM Central Time"
  schedule        = "0 10 * * *"  # 10:00 AM UTC = 5:00 AM Central
  time_zone       = "UTC"
  attempt_deadline = "600s"
  region          = var.region
  
  http_target {
    http_method = "POST"
    uri         = "https://discord-mirror-${var.region}.run.app/tasks/daily-wordle"
    
    oidc_token {
      service_account_email = google_service_account.discord_bot.email
      audience              = "https://discord-mirror-${var.region}.run.app"
    }
    
    headers = {
      "Content-Type" = "application/json"
    }
  }
}

# Cloud Scheduler Job for daily Weather (8:00 AM Central = 1:00 PM UTC)
resource "google_cloud_scheduler_job" "daily_weather" {
  name            = "discord-bot-daily-weather"
  description     = "Trigger daily weather report at 8:00 AM Central Time"
  schedule        = "0 13 * * *"  # 1:00 PM UTC = 8:00 AM Central
  time_zone       = "UTC"
  attempt_deadline = "600s"
  region          = var.region
  
  http_target {
    http_method = "POST"
    uri         = "https://discord-mirror-${var.region}.run.app/tasks/daily-weather"
    
    oidc_token {
      service_account_email = google_service_account.discord_bot.email
      audience              = "https://discord-mirror-${var.region}.run.app"
    }
    
    headers = {
      "Content-Type" = "application/json"
    }
  }
}
