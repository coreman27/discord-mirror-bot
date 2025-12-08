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
        date_str = today['date']  # Format: YYYY-MM-DD
        
        # Format date as "Monday, December 8, 2025"
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%A, %B %d, %Y')
        
        embed = discord.Embed(
            title=f"🌤️ Weather for {location}",
            description=f"**{formatted_date}**\n*{weather_desc}*",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        # Current conditions section
        embed.add_field(
            name="🌡️ Current Temperature", 
            value=f"**{temp_f}°F** (Feels like {feels_like_f}°F)", 
            inline=False
        )
        
        embed.add_field(name="📈 High", value=f"{max_temp}°F", inline=True)
        embed.add_field(name="📉 Low", value=f"{min_temp}°F", inline=True)
        embed.add_field(name="💧 Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="💨 Wind", value=f"{wind_speed} mph", inline=True)
        
        # Add spacing
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        # Process hourly data for Morning, Mid-Day, Afternoon, Night
        hourly = today['hourly']
        
        # Helper to find closest hour
        def get_forecast(time_str):
            for h in hourly:
                if h['time'] == time_str:
                    return h
            return None

        periods = [
            ("🌅 Morning (9AM)", "900"),
            ("☀️ Mid-Day (12PM)", "1200"),
            ("🌤️ Afternoon (3PM)", "1500"),
            ("🌙 Night (9PM)", "2100")
        ]

        for name, time_code in periods:
            forecast = get_forecast(time_code)
            if forecast:
                temp = forecast['tempF']
                rain = forecast['chanceofrain']
                desc = forecast['weatherDesc'][0]['value'].strip()
                embed.add_field(
                    name=name, 
                    value=f"**{temp}°F** • {rain}% rain\n*{desc}*", 
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

async def setup(bot):
    await bot.add_cog(Weather(bot))
