import discord
from discord.ext import commands, tasks
from discord import app_commands
import config
import aiohttp
import datetime
import pytz

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Dictionary to store scheduled locations: { "Location Name": channel_id }
        # Note: This is in-memory only and will reset on bot restart (Cloud Run is stateless)
        self.scheduled_locations = {
            "Houston, Texas": config.WEATHER_CHANNEL_ID,
            "Seattle, Washington": config.WEATHER_CHANNEL_ID,
            "Plano, Texas": config.WEATHER_CHANNEL_ID, 
        }
        self.daily_weather_task.start()

    def cog_unload(self):
        self.daily_weather_task.cancel()

    async def fetch_weather(self, location):
        """Fetches weather data from wttr.in"""
        url = f"https://wttr.in/{location}?format=j1"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None

    def create_weather_embed(self, data, location):
        """Creates a nice embed from wttr.in JSON data"""
        current = data['current_condition'][0]
        weather_desc = current['weatherDesc'][0]['value']
        temp_f = current['temp_F']
        feels_like_f = current['FeelsLikeF']
        humidity = current['humidity']
        wind_speed = current['windspeedMiles']
        
        # Get daily forecast for today
        today = data['weather'][0]
        max_temp = today['maxtempF']
        min_temp = today['mintempF']
        
        embed = discord.Embed(
            title=f"🌤️ Weather for {location}",
            description=f"**{weather_desc}**",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="Temperature", value=f"{temp_f}°F (Feels like {feels_like_f}°F)", inline=True)
        embed.add_field(name="High / Low", value=f"{max_temp}°F / {min_temp}°F", inline=True)
        embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="Wind", value=f"{wind_speed} mph", inline=True)

        # Process hourly data for Morning, Mid-Day, Afternoon, Night
        hourly = today['hourly']
        
        # Helper to find closest hour
        def get_forecast(time_str):
            for h in hourly:
                if h['time'] == time_str:
                    return h
            return None

        periods = [
            ("Morning (9AM)", "900"),
            ("Mid-Day (12PM)", "1200"),
            ("Afternoon (3PM)", "1500"),
            ("Night (9PM)", "2100")
        ]

        for name, time_code in periods:
            forecast = get_forecast(time_code)
            if forecast:
                temp = forecast['tempF']
                rain = forecast['chanceofrain']
                desc = forecast['weatherDesc'][0]['value']
                embed.add_field(
                    name=name, 
                    value=f"🌡️ {temp}°F\n💧 {rain}%\n{desc}", 
                    inline=True
                )
        
        embed.set_footer(text="Powered by wttr.in")
        return embed

    # Run daily at 8:00 AM Central Time
    @tasks.loop(time=datetime.time(hour=8, minute=0, tzinfo=pytz.timezone('US/Central')))
    async def daily_weather_task(self):
        print("Running daily weather task...")
        for location, channel_id in self.scheduled_locations.items():
            channel = self.bot.get_channel(channel_id)
            if channel:
                try:
                    data = await self.fetch_weather(location)
                    if data:
                        embed = self.create_weather_embed(data, location)
                        await channel.send(f"Good morning! Here is the weather for **{location}**:", embed=embed)
                    else:
                        print(f"Failed to fetch weather for {location}")
                except Exception as e:
                    print(f"Error sending weather for {location}: {e}")
            else:
                print(f"Could not find channel {channel_id} for weather")

    @app_commands.command(name="weather", description="Check the weather for a specific location")
    @app_commands.describe(location="City, State or Zip Code")
    @app_commands.guilds(config.GUILD_ID)
    async def weather(self, interaction: discord.Interaction, location: str):
        await interaction.response.defer()
        
        data = await self.fetch_weather(location)
        if data:
            embed = self.create_weather_embed(data, location)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"Sorry, I couldn't find weather data for '{location}'. Try 'City, State'.")

    @app_commands.command(name="subscribe_weather", description="Subscribe this channel to daily weather updates (Resets on bot restart)")
    @app_commands.describe(location="City, State to subscribe to")
    @app_commands.guilds(config.GUILD_ID)
    async def subscribe_weather(self, interaction: discord.Interaction, location: str):
        # Add to in-memory dictionary
        self.scheduled_locations[location] = interaction.channel_id
        
        await interaction.response.send_message(
            f"✅ Subscribed this channel to daily weather updates for **{location}** at 8:00 AM CST.\n"
            f"⚠️ **Note:** Since I run on the cloud, this subscription will be lost if I restart or redeploy. "
            f"Ask the developer to add it permanently if needed!"
        )

async def setup(bot):
    await bot.add_cog(Weather(bot))
