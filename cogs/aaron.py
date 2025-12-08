import discord
from discord.ext import commands
from discord import app_commands
import config

class Aaron(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = False

    @app_commands.command(name="toggle_aaron_hitler", description="Toggle the Aaron react feature on/off")
    @app_commands.guilds(config.GUILD_ID)
    async def toggle_aaron_hitler(self, interaction: discord.Interaction):
        if interaction.user.id not in [config.ADMIN_USER_ID, config.AEAERON_USER_ID]:
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return

        self.enabled = not self.enabled
        status = "enabled" if self.enabled else "disabled"
        await interaction.response.send_message(f"Aaron react feature is now **{status}**.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Feature: Aaron React
        if self.enabled and message.author.id == config.AEAERON_USER_ID:
            try:
                if message.guild:
                    emoji = discord.utils.get(message.guild.emojis, name="HitlerDaddy")
                    if emoji:
                        await message.add_reaction(emoji)
                    else:
                        print("Emoji 'HitlerDaddy' not found")
            except Exception as e:
                print(f"Error reacting to Aaron: {e}")

async def setup(bot):
    await bot.add_cog(Aaron(bot))
