import os
import discord
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SOURCE_CHANNEL_ID = int(os.getenv('SOURCE_CHANNEL_ID', 0))
DESTINATION_CHANNEL_ID = int(os.getenv('DESTINATION_CHANNEL_ID', 0))

# Initialize Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'Mirroring from channel {SOURCE_CHANNEL_ID} to {DESTINATION_CHANNEL_ID}')

@client.event
async def on_message(message):
    # Don't process messages sent by the bot itself to avoid loops
    if message.author == client.user:
        return

    # Check if the message is from the source channel
    if message.channel.id == SOURCE_CHANNEL_ID:
        try:
            destination_channel = client.get_channel(DESTINATION_CHANNEL_ID)
            
            if destination_channel:
                # Prepare the message content
                content = f"**{message.author.name}**: {message.content}"
                
                # Handle attachments (images, files)
                files = []
                for attachment in message.attachments:
                    # We need to read the file to send it again
                    # Note: For large files this might be slow/memory intensive
                    # A better approach for large files is to just send the url
                    if attachment.size < 8 * 1024 * 1024: # Limit to 8MB for safety
                        file_data = await attachment.to_file()
                        files.append(file_data)
                    else:
                        content += f"\n[Large attachment: {attachment.url}]"

                # Send the message to the destination channel
                await destination_channel.send(content=content, files=files, embeds=message.embeds)
                print(f"Mirrored message from {message.author.name}")
            else:
                print(f"Could not find destination channel with ID {DESTINATION_CHANNEL_ID}")
                
        except Exception as e:
            print(f"Error mirroring message: {e}")

if __name__ == "__main__":
    if not TOKEN or not SOURCE_CHANNEL_ID or not DESTINATION_CHANNEL_ID:
        print("Error: Please set DISCORD_TOKEN, SOURCE_CHANNEL_ID, and DESTINATION_CHANNEL_ID in .env file")
    else:
        client.run(TOKEN)
