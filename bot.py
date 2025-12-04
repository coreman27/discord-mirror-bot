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
        # We need to sync the tree, but since we are using Cogs, the commands are added to the tree automatically
        # However, we specified guild=GUILD_ID in the decorators, so they are guild-specific.
        # We can just sync the guild.
        bot.tree.copy_global_to(guild=config.GUILD_ID) # Just in case any global commands exist
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
            'cogs.general'
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
