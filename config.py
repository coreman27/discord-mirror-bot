import os
from dotenv import load_dotenv
import discord

load_dotenv()

# Environment Variables
TOKEN = os.getenv('DISCORD_TOKEN')
SOURCE_CHANNEL_ID = int(os.getenv('SOURCE_CHANNEL_ID', 0))
DESTINATION_CHANNEL_ID = int(os.getenv('DESTINATION_CHANNEL_ID', 0))
PORT = int(os.getenv('PORT', 8080))
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# User IDs
ADMIN_USER_ID = 313893805000753154
AEAERON_USER_ID = 102249538739245056
GUILD_ID = discord.Object(id=317792867953278976)
