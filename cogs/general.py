import discord
from discord.ext import commands
from discord import app_commands
import config

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="jeff", description="Get a summary of Jeff's features")
    @app_commands.guilds(config.GUILD_ID)
    async def jeff(self, interaction: discord.Interaction):
        # Access the Aaron cog to get the status
        aaron_cog = self.bot.get_cog('Aaron')
        
        features_list = "**Jeff's Features:**\n"
        features_list += "• **Message Mirroring**: I automatically copy messages from `raiders-of-the-lost-arc` to `raiders-of-the-lost-arc-unhinged`.\n"
        
        if aaron_cog and aaron_cog.enabled:
            features_list += f"• **Aaron React**: I react to Aaron's messages with the :HitlerDaddy: emoji. (Status: **Enabled**)\n"
            
        features_list += "• **Yapper Tracker**: Use `/yappers` to see who has sent the most messages recently."
        
        await interaction.response.send_message(features_list)

async def setup(bot):
    await bot.add_cog(General(bot))
