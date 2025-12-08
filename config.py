# INTERVIEW TOPIC: Configuration Management and Environment Variables
# Separating configuration from code follows the 12-Factor App methodology
# This allows different values for dev/staging/production without code changes

import os
from dotenv import load_dotenv  # Loads .env file into os.environ
import discord

# INTERVIEW TOPIC: Environment Variable Loading
# load_dotenv() reads the .env file and makes variables available via os.getenv()
# This is the standard way to manage secrets in Python applications
load_dotenv()

# INTERVIEW TOPIC: Environment Variables and Configuration
# Environment variables allow runtime configuration without hardcoding values
# Critical for: secrets management, multi-environment deployment, cloud services

# Secrets (should NEVER be committed to git)
TOKEN = os.getenv('DISCORD_TOKEN')  # Bot authentication token
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # AI service API key

# INTERVIEW TOPIC: Type Conversion and Default Values
# os.getenv() returns strings; int() converts them to integers
# Second parameter provides a default value if the environment variable is not set
MIRROR_SOURCE_CHANNEL_ID = int(os.getenv('MIRROR_SOURCE_CHANNEL_ID', 0))  # Channel to mirror from
MIRROR_DEST_CHANNEL_ID = int(os.getenv('MIRROR_DEST_CHANNEL_ID', 0))  # Channel to mirror to
WEATHER_CHANNEL_ID = int(os.getenv('WEATHER_CHANNEL_ID', 834901032273182800))  # Weather reports destination
PORT = int(os.getenv('PORT', 8080))  # HTTP server port for health checks

# INTERVIEW TOPIC: Application Constants
# Hardcoded IDs for user permissions and server identification
# These are non-sensitive and can be in code (unlike tokens/keys)
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', 313893805000753154))  # Admin with full permissions
AEAERON_USER_ID = int(os.getenv('AEAERON_USER_ID', 102249538739245056))  # Specific user for targeted features
GUILD_ID = discord.Object(id=int(os.getenv('GUILD_ID', 317792867953278976)))  # Discord server ID
