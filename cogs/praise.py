import discord
from discord.ext import commands
from discord import app_commands
import config
import random
import google.generativeai as genai

class Praise(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fallback_compliments = [
            "You light up the room just by being in it.",
            "You have a great sense of humor!",
            "You are more helpful than you realize.",
            "You have a really cool vibe.",
            "The world is better because you are in it.",
            "You are an awesome friend.",
            "I bet you make babies smile.",
            "You have the best ideas.",
            "You should be proud of yourself.",
            "You are a smart cookie!",
            "I appreciate you.",
            "You are enough, just as you are.",
            "You are a ray of sunshine on a cloudy day."
        ]
        
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None

    @app_commands.command(name="praise", description="Deliver a context-aware compliment to a user")
    @app_commands.describe(user="The user to praise")
    @app_commands.guilds(config.GUILD_ID)
    async def praise(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer(thinking=True)

        if not self.model:
            # Fallback if no API key
            compliment = random.choice(self.fallback_compliments)
            await interaction.followup.send(f"{user.mention} {compliment} (AI unavailable, using fallback)")
            return

        try:
            # Fetch recent chat history for context
            history = []
            async for msg in interaction.channel.history(limit=100):
                if not msg.content:
                    continue
                history.append(f"{msg.author.display_name}: {msg.content}")
            
            # Reverse to chronological order
            history.reverse()
            transcript = "\n".join(history)

            if user.id == self.bot.user.id:
                prompt = (
                    f"You have been asked to praise YOURSELF (the bot). Based on the chat history (if relevant) or just your nature as a bot, "
                    f"write a short, humble, and grateful message thanking the users for having you. "
                    f"Mention how much you love serving this server. "
                    f"Keep it under 280 characters.\n\n"
                    f"Chat History:\n{transcript}"
                )
            else:
                prompt = (
                    f"You are a wholesome and encouraging friend. Based on the following chat history, write a short, "
                    f"heartfelt, and specific compliment targeting the user '{user.display_name}'. "
                    f"Use the context of what they said or what others said to them to make it personal. "
                    f"Keep it under 280 characters. Be sincere and kind.\n\n"
                    f"Chat History:\n{transcript}"
                )

            response = await self.model.generate_content_async(prompt)
            praise_text = response.text

            await interaction.followup.send(f"{user.mention} {praise_text}")

        except Exception as e:
            print(f"Error generating praise: {e}")
            # Fallback on error
            compliment = random.choice(self.fallback_compliments)
            await interaction.followup.send(f"{user.mention} {compliment} (AI error: {str(e)})")

async def setup(bot):
    await bot.add_cog(Praise(bot))
