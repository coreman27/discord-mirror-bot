# Discord Channel Mirror Bot

This script listens to messages in one Discord channel and automatically posts a copy of them to another channel.

## Setup

1.  **Install Python**: Ensure you have Python installed.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    *   Rename `.env.example` to `.env`.
    *   Open `.env` and fill in your details:
        *   `DISCORD_TOKEN`: Your Discord Bot Token (get this from the [Discord Developer Portal](https://discord.com/developers/applications)).
        *   `SOURCE_CHANNEL_ID`: The ID of the channel you want to copy messages *from*.
        *   `DESTINATION_CHANNEL_ID`: The ID of the channel you want to paste messages *to*.
    *   *Tip: To get Channel IDs, enable "Developer Mode" in Discord settings (under Advanced), then right-click a channel and select "Copy ID".*

## Running Locally

Run the script:

```bash
python bot.py
```

## Deployment (Google Cloud)

This project includes Terraform configuration to set up a Cloud Build trigger and Secret Manager secrets.

### Prerequisites

1.  A Google Cloud Project.
2.  [Terraform installed](https://developer.hashicorp.com/terraform/downloads).
3.  [Google Cloud SDK installed](https://cloud.google.com/sdk/docs/install).
4.  Connect your GitHub repository to Cloud Build in the GCP Console: [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers).

### Steps

1.  **Initialize Git**:
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    # Add your remote origin
    git remote add origin <your-github-repo-url>
    git push -u origin main
    ```

2.  **Deploy Infrastructure**:
    Navigate to the `terraform` directory:
    ```bash
    cd terraform
    terraform init
    ```

    Create a `terraform.tfvars` file with your secrets (DO NOT COMMIT THIS FILE):
    ```hcl
    project_id             = "your-project-id"
    github_owner           = "your-github-username"
    github_repo            = "your-repo-name"
    discord_token          = "your-bot-token"
    source_channel_id      = "123456789"
    destination_channel_id = "987654321"
    ```

    Apply the configuration:
    ```bash
    terraform apply
    ```

    This will:
    *   Create secrets in Google Secret Manager for your token and channel IDs.
    *   Grant necessary permissions to Cloud Build and Cloud Run service accounts.
    *   Create a Cloud Build Trigger that deploys the bot whenever you push to `main`.

3.  **Trigger Deployment**:
    Push a change to your repository to trigger the first build and deployment.
