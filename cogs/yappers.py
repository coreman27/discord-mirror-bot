import discord
from discord.ext import commands
from discord import app_commands
import config

class Yappers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="yappers", description="See who talks the most (scans last 2000 messages)")
    @app_commands.guilds(config.GUILD_ID)
    async def yappers(self, interaction: discord.Interaction):
        # Defer the response because reading history takes more than 3 seconds
        await interaction.response.defer(thinking=True)
        
        message_counts = {}
        total_scanned = 0
        
        try:
            # Scan history (limit to 2000 to prevent timeouts)
            async for msg in interaction.channel.history(limit=2000):
                # Skip bots
                if msg.author.bot:
                    continue
                
                total_scanned += 1
                author_name = msg.author.display_name
                message_counts[author_name] = message_counts.get(author_name, 0) + 1
            
            if not message_counts:
                await interaction.followup.send("No messages found to count!")
                return

            # Sort by count (highest first)
            sorted_yappers = sorted(message_counts.items(), key=lambda item: item[1], reverse=True)
            
            # Format output
            output = f"**🏆 Top Yappers (Last {total_scanned} messages)**\n"
            for i, (name, count) in enumerate(sorted_yappers[:5], 1):
                output += f"**{i}. {name}**: {count} messages\n"
                
            await interaction.followup.send(output)
            
        except Exception as e:
            await interaction.followup.send(f"Error counting yaps: {e}")

async def setup(bot):
    await bot.add_cog(Yappers(bot))
