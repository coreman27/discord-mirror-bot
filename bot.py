# INTERVIEW TOPIC: Module Imports and Dependencies
# - asyncio: Built-in Python library for asynchronous I/O operations
# - discord/discord.ext: Third-party library for Discord API interaction
# - aiohttp: Async HTTP client/server framework (used for health checks)
# - config: Custom module containing environment variables and configuration
import asyncio
import discord
from discord.ext import commands
from aiohttp import web
import config

# INTERVIEW TOPIC: Object Initialization and Configuration
# Initialize Discord Bot with intents (permissions for what events the bot can receive)
# Intents are a security feature that controls what data your bot has access to
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content (not just metadata)
bot = commands.Bot(command_prefix="!", intents=intents)

# INTERVIEW TOPIC: Async Functions and Coroutines
# 'async def' defines a coroutine function that can use 'await' for non-blocking I/O
# Coroutines are functions that can pause execution and resume later
async def health_check(request):
    """Health check endpoint for Cloud Run to verify the service is alive.
    
    INTERVIEW TOPIC: Cloud Platform Integration
    Cloud Run requires HTTP endpoints to determine if a container is healthy.
    This simple endpoint returns 200 OK to indicate the service is running.
    """
    return web.Response(text="OK")

async def daily_wordle_endpoint(request):
    """HTTP endpoint for Cloud Task to trigger daily Wordle solving.
    
    Called by Cloud Scheduler → Cloud Task
    """
    try:
        # Get the Wordle cog from the bot
        wordle_cog = bot.get_cog('Wordle')
        if not wordle_cog:
            return web.Response(text="Wordle cog not loaded", status=503)
        
        # Call the task handler
        await wordle_cog.run_daily_wordle()
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"Error in daily_wordle_endpoint: {e}")
        import traceback
        traceback.print_exc()
        return web.Response(text=f"Error: {str(e)}", status=500)

async def daily_weather_endpoint(request):
    """HTTP endpoint for Cloud Task to trigger daily weather posting.
    
    Called by Cloud Scheduler → Cloud Task
    """
    try:
        # Get the Weather cog from the bot
        weather_cog = bot.get_cog('Weather')
        if not weather_cog:
            return web.Response(text="Weather cog not loaded", status=503)
        
        # Call the task handler
        await weather_cog.run_daily_weather()
        return web.Response(text="OK", status=200)
    except Exception as e:
        print(f"Error in daily_weather_endpoint: {e}")
        import traceback
        traceback.print_exc()
        return web.Response(text=f"Error: {str(e)}", status=500)

async def start_server():
    """Start an HTTP server alongside the Discord bot.
    
    INTERVIEW TOPIC: Concurrent Services Pattern
    Running multiple services (Discord bot + HTTP server) in the same process
    allows Cloud Run to perform health checks while the bot handles Discord events.
    """
    app = web.Application()  # Create aiohttp web application
    app.router.add_get('/', health_check)  # Register route handler
    app.router.add_post('/tasks/daily-wordle', daily_wordle_endpoint)  # Wordle task
    app.router.add_post('/tasks/daily-weather', daily_weather_endpoint)  # Weather task
    runner = web.AppRunner(app)  # Create application runner
    await runner.setup()  # Initialize the runner (async setup)
    # INTERVIEW TOPIC: Network Binding
    # '0.0.0.0' means listen on all network interfaces (required for containers)
    site = web.TCPSite(runner, '0.0.0.0', config.PORT)
    await site.start()  # Non-blocking start using await
    print(f"HTTP server started on port {config.PORT}")

# INTERVIEW TOPIC: Decorators and Event-Driven Programming
# @bot.event is a decorator that registers this function as an event handler
# Decorators modify function behavior without changing the function's code
@bot.event
async def on_ready():
    """Event handler called when the bot successfully connects to Discord.
    
    INTERVIEW TOPIC: Lifecycle Hooks
    on_ready() is a lifecycle hook - a callback invoked at a specific point
    in the application's lifecycle (similar to React's useEffect or Angular's ngOnInit)
    """
    print(f'{bot.user} has connected to Discord!')
    print(f'Mirroring from channel {config.MIRROR_SOURCE_CHANNEL_ID} to {config.MIRROR_DEST_CHANNEL_ID}')
    
    # INTERVIEW TOPIC: Error Handling and Graceful Degradation
    # Try-except blocks prevent critical failures from crashing the entire application
    try:
        # INTERVIEW TOPIC: API Synchronization
        # Discord requires explicit command registration (sync) before slash commands work
        # Global sync clears old commands, guild sync registers new ones instantly
        await bot.tree.sync()  # Clear global commands
        print("Global commands synced (cleared)")

        await bot.tree.sync(guild=config.GUILD_ID)  # Register guild-specific commands
        print(f"Slash commands synced to guild {config.GUILD_ID.id}")
    except Exception as e:
        # INTERVIEW TOPIC: Defensive Programming
        # Catch and log errors instead of crashing - allows bot to continue functioning
        print(f"Failed to sync commands: {e}")

    # Start the HTTP server when the bot is ready
    await start_server()

async def main():
    """Main entry point for the Discord bot.
    
    INTERVIEW TOPIC: Async Context Managers
    'async with' is an async context manager - ensures proper setup and teardown
    Similar to 'with open()' for files, but works with async resources
    """
    async with bot:
        # INTERVIEW TOPIC: Plugin Architecture (Modular Design)
        # Cogs are Discord.py's way of organizing commands into separate modules
        # This follows the Single Responsibility Principle - each cog handles one feature
        extensions = [
            'cogs.mirroring',   # Message forwarding between channels
            'cogs.yappers',     # Message statistics tracking
            'cogs.general',     # General utility commands
            'cogs.roast',       # AI-powered roasting
            'cogs.praise',      # AI-powered compliments
            'cogs.weather',     # Weather reports and scheduling
            'cogs.wordle'       # Wordle auto-solver with trial-and-error
        ]
        
        # INTERVIEW TOPIC: Iteration and Error Handling
        # Load each extension individually, catching errors to prevent one failure
        # from stopping the entire bot (fail-safe pattern)
        for ext in extensions:
            try:
                await bot.load_extension(ext)
                print(f"Loaded extension: {ext}")
            except Exception as e:
                # INTERVIEW TOPIC: Graceful Degradation
                # Log the error but continue loading other extensions
                print(f"Failed to load extension {ext}: {e}")
        
        # INTERVIEW TOPIC: Input Validation and Early Returns
        # Validate configuration before attempting to connect
        # Early return pattern prevents deeper execution with invalid state
        if not config.TOKEN:
            print("Error: Please set DISCORD_TOKEN in .env file")
            return
            
        # INTERVIEW TOPIC: Async I/O
        # bot.start() is a long-running async operation that connects to Discord
        # and keeps the connection alive until the program terminates
        await bot.start(config.TOKEN)

# INTERVIEW TOPIC: Python Entry Point Pattern
# if __name__ == "__main__" ensures this code only runs when executed directly
# (not when imported as a module). This is Python's way of defining a main function.
if __name__ == "__main__":
    # INTERVIEW TOPIC: Event Loop Management
    # asyncio.run() creates a new event loop, runs the coroutine, and cleans up
    # The event loop is the core of async Python - it schedules and executes async tasks
    asyncio.run(main())
