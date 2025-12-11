import traceback
import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):
    """Global handler to ensure deferred interactions always receive a reply on error."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction: discord.Interaction, error: Exception):
        # Log full traceback to console for debugging
        print("Unhandled application command error:")
        traceback.print_exception(type(error), error, error.__traceback__)

        # Try to notify the user in the channel / interaction so 'thinking' doesn't stay forever
        try:
            # If we've already deferred the response, use followup
            if interaction.response.is_done():
                await interaction.followup.send("An internal error occurred while processing your command. The maintainers have been notified.", ephemeral=True)
            else:
                # Otherwise send an immediate response
                await interaction.response.send_message("An internal error occurred while processing your command. The maintainers have been notified.", ephemeral=True)
        except Exception as send_err:
            # If we can't send to the interaction (bot shutting down etc.), just log
            print(f"Failed to send error response to interaction: {send_err}")


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
