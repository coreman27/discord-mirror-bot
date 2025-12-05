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
        features_list = "**Jeff's Features:**\n"
        
        # Check for Mirroring Cog
        if self.bot.get_cog('Mirroring'):
            features_list += "• **Message Mirroring**: I automatically copy messages from `raiders-of-the-lost-arc` to `raiders-of-the-lost-arc-unhinged`.\n"
        
        # Check for Aaron Cog
        aaron_cog = self.bot.get_cog('Aaron')
        if aaron_cog:
            status = "Enabled" if aaron_cog.enabled else "Disabled"
            features_list += f"• **Aaron React**: I react to Aaron's messages with the :HitlerDaddy: emoji. (Status: **{status}**)\n"
            
        # Check for Yappers Cog
        if self.bot.get_cog('Yappers'):
            features_list += "• **Yapper Tracker**: Use `/yappers` to see who has sent the most messages recently.\n"
            
        # Check for Roast Cog
        if self.bot.get_cog('Roast'):
            features_list += "• **Roast**: Use `/roast @user` to deliver a context-aware burn based on recent chat history (AI-powered).\n"

        # Check for Praise Cog
        if self.bot.get_cog('Praise'):
            features_list += "• **Praise**: Use `/praise @user` to deliver a wholesome compliment based on recent chat history (AI-powered)."
        
        await interaction.response.send_message(features_list)

async def setup(bot):
    await bot.add_cog(General(bot))
