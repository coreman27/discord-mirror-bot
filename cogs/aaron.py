import discord
from discord.ext import commands
from discord import app_commands
import config

# INTERVIEW TOPIC: Object-Oriented Programming - Classes and Inheritance
# Cog is a Discord.py concept for organizing bot commands and event listeners
# Inheriting from commands.Cog provides the structure Discord.py expects
class Aaron(commands.Cog):
    """Cog for Aaron-specific features (automated reactions).
    
    INTERVIEW TOPIC: Class Design and State Management
    This class demonstrates:
    - Instance variables for state (self.enabled)
    - Dependency injection (bot passed to constructor)
    - Encapsulation (feature logic isolated in one class)
    """
    
    def __init__(self, bot):
        """Initialize the Aaron cog.
        
        INTERVIEW TOPIC: Constructor Pattern
        __init__ is Python's constructor - called when creating a new instance
        """
        self.bot = bot  # Store bot reference for later use
        self.enabled = False  # Feature flag - controls if feature is active

    # INTERVIEW TOPIC: Decorators and Metadata
    # Decorators add metadata/behavior to functions without modifying their code
    @app_commands.command(name="toggle_aaron_hitler", description="Toggle the Aaron react feature on/off")
    @app_commands.guilds(config.GUILD_ID)  # Restrict command to specific Discord server
    async def toggle_aaron_hitler(self, interaction: discord.Interaction):
        """Toggle the Aaron reaction feature on/off.
        
        INTERVIEW TOPIC: Authorization and Access Control
        Implements role-based access control (RBAC) by checking user IDs
        """
        # INTERVIEW TOPIC: Authentication vs Authorization
        # Check if user is authorized (has permission) to use this command
        if interaction.user.id not in [config.ADMIN_USER_ID, config.AEAERON_USER_ID]:
            # ephemeral=True makes the message visible only to the user who ran the command
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return  # Early return prevents unauthorized access

        # INTERVIEW TOPIC: State Toggle Pattern
        # Toggle boolean state using 'not' operator (common pattern in feature flags)
        self.enabled = not self.enabled
        
        # INTERVIEW TOPIC: Ternary Operator (Conditional Expression)
        # Shorthand for if-else: value_if_true if condition else value_if_false
        status = "enabled" if self.enabled else "disabled"
        
        # INTERVIEW TOPIC: String Formatting (f-strings)
        # f"..." allows embedding expressions inside strings using {variable}
        await interaction.response.send_message(f"Aaron react feature is now **{status}**.")

    # INTERVIEW TOPIC: Event-Driven Programming and Listeners
    # @commands.Cog.listener() registers this method as an event handler
    # It will be called automatically whenever a message is sent in Discord
    @commands.Cog.listener()
    async def on_message(self, message):
        """Event handler that fires for every message sent in Discord.
        
        INTERVIEW TOPIC: Event Handlers and Callbacks
        This is a callback function - it doesn't get called directly by our code,
        but by the Discord.py library when a specific event (message) occurs.
        """
        # INTERVIEW TOPIC: Guard Clauses and Early Returns
        # Prevent infinite loops - don't react to the bot's own messages
        if message.author == self.bot.user:
            return

        # INTERVIEW TOPIC: Conditional Logic and Short-Circuit Evaluation
        # Multiple conditions: only proceed if enabled AND message is from target user
        # Python evaluates left-to-right and stops if any condition is False (short-circuit)
        if self.enabled and message.author.id == config.AEAERON_USER_ID:
            # INTERVIEW TOPIC: Exception Handling and Defensive Programming
            # Wrap risky operations in try-except to prevent crashes
            try:
                # Ensure message is in a server (not a DM) before accessing custom emojis
                if message.guild:
                    # INTERVIEW TOPIC: Searching Collections
                    # discord.utils.get() searches a collection for an item matching criteria
                    emoji = discord.utils.get(message.guild.emojis, name="HitlerDaddy")
                    
                    # INTERVIEW TOPIC: Null/None Checking
                    # Always check if a search returned a result before using it
                    if emoji:
                        # INTERVIEW TOPIC: Async Operations
                        # await pauses execution until the Discord API responds
                        await message.add_reaction(emoji)
                    else:
                        # INTERVIEW TOPIC: Logging and Observability
                        # Log when something fails to help with debugging
                        print("Emoji 'HitlerDaddy' not found")
            except Exception as e:
                # INTERVIEW TOPIC: Error Logging
                # Catch-all exception handler logs errors without crashing
                # In production, you'd use proper logging (logging module) instead of print
                print(f"Error reacting to Aaron: {e}")

# INTERVIEW TOPIC: Module Setup Functions and Plugin Architecture
# Discord.py calls setup() when loading this cog as an extension
async def setup(bot):
    """Required function for Discord.py extension loading.
    
    INTERVIEW TOPIC: Dependency Injection and Inversion of Control
    The bot instance is injected here, following IoC principle
    """
    await bot.add_cog(Aaron(bot))  # Register the cog with the bot
