import discord
from discord.ext import commands
from discord import app_commands
import config

class Mirroring(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Don't process messages sent by the bot itself
        if message.author == self.bot.user:
            return

        # Check if the message is from the source channel
        if message.channel.id == config.SOURCE_CHANNEL_ID:
            try:
                destination_channel = self.bot.get_channel(config.DESTINATION_CHANNEL_ID)
                
                if destination_channel:
                    # Prepare the message content
                    content = f"**{message.author.name}**: {message.content}"
                    
                    # Handle attachments (images, files)
                    files = []
                    for attachment in message.attachments:
                        if attachment.size < 8 * 1024 * 1024: # Limit to 8MB
                            file_data = await attachment.to_file()
                            files.append(file_data)
                        else:
                            content += f"\n[Large attachment: {attachment.url}]"

                    # Send the message to the destination channel
                    await destination_channel.send(content=content, files=files, embeds=message.embeds)
                    print(f"Mirrored message from {message.author.name}")
                else:
                    print(f"Could not find destination channel with ID {config.DESTINATION_CHANNEL_ID}")
                    
            except Exception as e:
                print(f"Error mirroring message: {e}")

async def setup(bot):
    await bot.add_cog(Mirroring(bot))
