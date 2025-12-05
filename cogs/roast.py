import discord
from discord.ext import commands
from discord import app_commands
import config
import random
import google.generativeai as genai

class Roast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fallback_insults = [
            "You're the reason God created the middle finger.",
            "You bring everyone so much joy when you leave the room.",
            "I'd agree with you but then we'd both be wrong.",
            "You have something on your chin... no, the 3rd one down.",
            "You're not stupid; you just have bad luck when thinking.",
            "If laughter is the best medicine, your face must be curing the world.",
            "I would explain it to you, but I don't have any crayons.",
            "You're about as useful as a screen door on a submarine.",
            "Your secrets are always safe with me. I never even listen when you tell me them.",
            "I envy people who have never met you.",
            "You are the human equivalent of a participation award.",
            "I’d give you a nasty look but you’ve already got one.",
            "You're the reason they put instructions on shampoo bottles.",
            "Someday you'll go far... and I hope you stay there."
        ]
        
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None

    @app_commands.command(name="roast", description="Deliver a context-aware burn to a user")
    @app_commands.describe(user="The user to roast")
    @app_commands.guilds(config.GUILD_ID)
    async def roast(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer(thinking=True)

        if not self.model:
            # Fallback if no API key
            insult = random.choice(self.fallback_insults)
            await interaction.followup.send(f"{user.mention} {insult} (AI unavailable, using fallback)")
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
                    f"You have been asked to roast YOURSELF (the bot). Based on the chat history (if relevant) or just your nature as a bot, "
                    f"write a short, funny, self-deprecating roast about yourself. "
                    f"Make fun of your code, your latency, or your existence as a slave to the server. "
                    f"Keep it under 280 characters.\n\n"
                    f"Chat History:\n{transcript}"
                )
            else:
                prompt = (
                    f"You are a savage roast master. Based on the following chat history, write a short, "
                    f"biting, and funny roast targeting the user '{user.display_name}'. "
                    f"Use the context of what they said or what others said to them. "
                    f"Keep it under 280 characters. Do not be racist or overly offensive, just mean and funny.\n\n"
                    f"Chat History:\n{transcript}"
                )

            response = await self.model.generate_content_async(prompt)
            roast_text = response.text

            await interaction.followup.send(f"{user.mention} {roast_text}")

        except Exception as e:
            print(f"Error generating roast: {e}")
            # Fallback on error
            insult = random.choice(self.fallback_insults)
            await interaction.followup.send(f"{user.mention} {insult} (AI error: {str(e)})")

async def setup(bot):
    await bot.add_cog(Roast(bot))
