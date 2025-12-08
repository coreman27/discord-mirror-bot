import asyncio
import discord
from discord.ext import commands
from aiohttp import web
import config

# Initialize Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def health_check(request):
    return web.Response(text="OK")

async def start_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', config.PORT)
    await site.start()
    print(f"HTTP server started on port {config.PORT}")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Mirroring from channel {config.SOURCE_CHANNEL_ID} to {config.DESTINATION_CHANNEL_ID}')
    
    # Sync slash commands to the specific guild for instant updates
    try:
        # 1. Sync global commands to clear any old/stale global commands (fixes duplicates)
        await bot.tree.sync()
        print("Global commands synced (cleared)")

        # 2. Sync guild-specific commands
        await bot.tree.sync(guild=config.GUILD_ID)
        print(f"Slash commands synced to guild {config.GUILD_ID.id}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    # Start the HTTP server when the bot is ready
    await start_server()

async def main():
    async with bot:
        # Load extensions
        extensions = [
            'cogs.mirroring',
            'cogs.aaron',
            'cogs.yappers',
            'cogs.general',
            'cogs.roast',
            'cogs.praise',
            'cogs.weather'
        ]
        
        for ext in extensions:
            try:
                await bot.load_extension(ext)
                print(f"Loaded extension: {ext}")
            except Exception as e:
                print(f"Failed to load extension {ext}: {e}")
        
        if not config.TOKEN:
            print("Error: Please set DISCORD_TOKEN in .env file")
            return
            
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
