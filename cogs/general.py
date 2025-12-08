import discord
from discord.ext import commands
from discord import app_commands
import config
from .features import FEATURES

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="jeff", description="Get a summary of Jeff's features")
    @app_commands.guilds(config.GUILD_ID)
    async def jeff(self, interaction: discord.Interaction):
        features_list = "**Jeff's Features:**\n"
        
        # Check for Mirroring Cog
        if self.bot.get_cog('Mirroring'):
            features_list += FEATURES['Mirroring'] + "\n"
        
        # Check for Aaron Cog
        if self.bot.get_cog('Aaron'):
            status = "Enabled" if aaron_cog.enabled else "Disabled"
            features_list += FEATURES['Aaron'].format(status=status) + "\n"
            
        # Check for Yappers Cog
        if self.bot.get_cog('Yappers'):
            features_list += FEATURES['Yappers'] + "\n"
            
        # Check for Roast Cog
        if self.bot.get_cog('Roast'):
            features_list += FEATURES['Roast'] + "\n"

        # Check for Praise Cog
        if self.bot.get_cog('Praise'):
            features_list += FEATURES['Praise'] + "\n"
        
        # Check for Weather Cog
        if self.bot.get_cog('Weather'):
            features_list += FEATURES['Weather']
        
        await interaction.response.send_message(features_list)

async def setup(bot):
    await bot.add_cog(General(bot))
