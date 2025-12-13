import discord
from discord.ext import commands
from discord import app_commands
import config
import datetime
import pytz
import asyncio

# Import the WordleSolver
try:
    from services.wordle_solver import WordleSolver
except ImportError:
    print("Warning: Could not import WordleSolver. Wordle cog will not work.")
    WordleSolver = None

class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Removed: self.daily_wordle_task.start()

    def cog_unload(self):
        pass
        # Removed: self.daily_wordle_task.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):
        # React to Wordle posts with 💯 and additional reactions
        if "Wordle" in message.content:
            print(f"Detected Wordle message from {message.author}: {message.content[:20]}...")
            try:
                await message.add_reaction("💯")
                
                # Parse the Wordle message for additional reactions
                lines = message.content.strip().split('\n')
                if len(lines) < 2:
                    return
                
                # Find the header line (it might not be the first line if there's whitespace)
                header = None
                import re
                for line in lines:
                    if line.strip().startswith("Wordle"):
                        header = line.strip()
                        break
                
                if not header:
                    return

                match = re.search(r'Wordle\s+([\d,]+)\s+([X\d]+)/6\*?', header)
                if not match:
                    return
                
                attempts_str = match.group(2)
                solved = attempts_str != 'X'
                if solved:
                    attempts = int(attempts_str)
                else:
                    attempts = 7  # Failed, so more than 6
                
                # Check for no yellows in the grid for perfect solve
                grid_lines = [line for line in lines[1:] if line.strip() and any(c in line for c in ['🟩','🟨','⬛','⬜'])]
                has_yellow = any('🟨' in line for line in grid_lines)
                
                if not solved:
                    # Failed Wordle
                    await message.add_reaction("😭")  # :sob:
                else:
                    if not has_yellow:
                        await message.add_reaction("🟩")  # :green_square:
                    
                    # React based on number of attempts
                    if attempts == 1:
                        await message.add_reaction("🥇")  # :first_place:
                    elif attempts == 2:
                        await message.add_reaction("🥈")  # :second_place:
                    elif attempts == 3:
                        await message.add_reaction("🥉")  # :third_place:
                        
            except Exception as e:
                print(f"Failed to react to Wordle message: {e}")
                print(f"Failed to react to Wordle message: {e}")

    # Run daily at 5:00 AM Central Time (called by Cloud Task via HTTP endpoint)
    async def run_daily_wordle(self):
        """Called by HTTP endpoint from Cloud Task scheduler"""
        print(f"Running daily Wordle task at {datetime.datetime.now()}")
        
        if WordleSolver is None:
            print("WordleSolver not available, skipping.")
            return
        
        channel = self.bot.get_channel(config.WORDLE_CHANNEL_ID)
        if not channel:
            print(f"❌ Could not find Wordle channel {config.WORDLE_CHANNEL_ID}")
            return
        
        try:
            print("Starting Wordle solver...")
            def _run_solver():
                # Use regular Chrome driver for Cloud Run stability
                s = WordleSolver(headless=True, use_undetected=False)
                success = s.solve(max_guesses=6)
                # Result is already captured in s.share_text during solve()
                return success, s.share_text

            success, share_text = await asyncio.to_thread(_run_solver)
            
            if share_text:
                await channel.send(f"{share_text}")
                if success:
                    print("✅ Successfully posted Wordle result")
                else:
                    print("⚠️ Posted failed Wordle result")
            elif success:
                await channel.send("Daily Wordle solved, but couldn't capture the result.")
            else:
                await channel.send("Failed to solve today's Wordle within 6 guesses and couldn't capture result.")
                
        except Exception as e:
            print(f"❌ Error in Wordle task: {e}")
            import traceback
            traceback.print_exc()

    @app_commands.command(name="wordle", description="Solve today's Wordle manually")
    @app_commands.guilds(config.GUILD_ID)
    async def wordle_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if WordleSolver is None:
            await interaction.followup.send("Wordle solver not available.")
            return
        
        try:
            def _run_solver_cmd():
                s = WordleSolver(headless=True)
                success = s.solve(max_guesses=6)
                # Result is already captured in s.share_text during solve()
                return success, s.share_text

            success, share_text = await asyncio.to_thread(_run_solver_cmd)
            
            if share_text:
                await interaction.followup.send(f"{share_text}")
            elif success:
                await interaction.followup.send("Wordle solved, but couldn't capture the result.")
            else:
                await interaction.followup.send("Failed to solve today's Wordle within 6 guesses and couldn't capture result.")
                
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)[:1000]}")  # Limit length

async def setup(bot):
    await bot.add_cog(Wordle(bot))