import discord
from discord.ext import commands
from discord import app_commands
import config
import aiohttp
import datetime
import asyncio
import time

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # List of locations to post weather for each morning
        self.scheduled_locations = [
            "Houston, Texas",
            "Portland, Oregon",
            "Winston-Salem, North Carolina",
            "Plano, Texas"
        ]
        # Removed: self.daily_weather_task.start()

    def cog_unload(self):
        pass
        # Removed: self.daily_weather_task.cancel()

    async def fetch_weather(self, location):
        """Fetches weather data from wttr.in"""
        import urllib.parse
        encoded_location = urllib.parse.quote(location)
        url = f"https://wttr.in/{encoded_location}?format=j1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # Retry with exponential backoff on transient errors
        attempts = 3
        backoff = 1
        for attempt in range(1, attempts + 1):
            start_time = time.time()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=20), allow_redirects=True) as response:
                        elapsed = time.time() - start_time
                        status = response.status
                        content_type = response.headers.get('Content-Type', 'unknown')
                        
                        print(f"🔍 Attempt {attempt} for {location}: Status={status}, Content-Type={content_type}, Time={elapsed:.2f}s")
                        
                        if status != 200:
                            text = await response.text()
                            print(f"⚠️ Attempt {attempt}: Failed to fetch weather for {location}: Status {status}. Response snippet: {text[:500]!r}")
                            # Retry for 5xx server errors
                            if 500 <= status < 600 and attempt < attempts:
                                await asyncio.sleep(backoff)
                                backoff *= 2
                                continue
                            return None

                        # Check if we got JSON content-type
                        if 'application/json' not in content_type.lower():
                            text = await response.text()
                            print(f"⚠️ Attempt {attempt}: Unexpected content-type '{content_type}' for {location}. Response snippet: {text[:500]!r}")
                            # Retry on HTML responses as wttr.in might be having issues
                            if attempt < attempts:
                                await asyncio.sleep(backoff)
                                backoff *= 2
                                continue
                            return None

                        try:
                            return await response.json()
                        except (aiohttp.ContentTypeError, ValueError) as json_err:
                            text = await response.text()
                            print(f"⚠️ Attempt {attempt}: Failed to parse JSON for {location} ({type(json_err).__name__}). Response snippet: {text[:500]!r}")
                            # Retry JSON parse errors
                            if attempt < attempts:
                                await asyncio.sleep(backoff)
                                backoff *= 2
                                continue
                            return None
                            
            except asyncio.TimeoutError:
                elapsed = time.time() - start_time
                print(f"⏱️ Attempt {attempt}: TIMEOUT after {elapsed:.2f}s fetching weather for {location}")
                if attempt < attempts:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                return None
            except aiohttp.ClientError as e:
                elapsed = time.time() - start_time
                print(f"🌐 Attempt {attempt}: Network error after {elapsed:.2f}s for {location}: {type(e).__name__}: {e}")
                if attempt < attempts:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                return None
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ Attempt {attempt}: Unexpected error after {elapsed:.2f}s for {location}: {type(e).__name__}: {repr(e)}")
                if attempt < attempts:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                return None

    def create_weather_embed(self, data, location):
        """Creates a nice embed from wttr.in JSON data"""
        try:
            current = data.get('current_condition', [])[0]
            weather_desc = current.get('weatherDesc', [{}])[0].get('value', 'N/A')
            temp_f = current.get('temp_F', 'N/A')
            feels_like_f = current.get('FeelsLikeF', 'N/A')
            humidity = current.get('humidity', 'N/A')
            wind_speed = current.get('windspeedMiles', 'N/A')

            # Get daily forecast for today
            today = data.get('weather', [])[0]
            max_temp = today.get('maxtempF', 'N/A')
            min_temp = today.get('mintempF', 'N/A')
            date_str = today.get('date', '')  # Format: YYYY-MM-DD

            # Format date as "Monday, December 8, 2025" if available
            if date_str:
                try:
                    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%A, %B %d, %Y')
                except Exception:
                    formatted_date = date_str
            else:
                formatted_date = 'Today'

            embed = discord.Embed(
                title=f"🌤️ Weather for {location}",
                description=f"**{formatted_date}**\n*{weather_desc}*",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
        except Exception as e:
            print(f"❌ Error creating embed for {location}: {e}")
            raise
        
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
            # wttr.in hourly 'time' values are often '0','300','600','900','1200' etc.
            # Attempt an exact match first, otherwise pick the closest hour available.
            for h in hourly:
                if str(h.get('time', '')) == str(time_str):
                    return h

            try:
                target = int(time_str)
            except Exception:
                return None

            best = None
            best_diff = None
            for h in hourly:
                try:
                    t = int(h.get('time', 0))
                except Exception:
                    continue
                diff = abs(t - target)
                if best is None or diff < best_diff:
                    best = h
                    best_diff = diff
            return best

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

    # Run daily at 4:00 AM Central Time (called by Cloud Task via HTTP endpoint)
    async def run_daily_weather(self):
        """Called by HTTP endpoint from Cloud Task scheduler"""
        print(f"Running daily weather task at {datetime.datetime.now()}")
        print(f"Scheduled locations: {self.scheduled_locations}")
        
        # Get the channel once (all locations post to the same channel)
        channel = self.bot.get_channel(config.WEATHER_CHANNEL_ID)
        if not channel:
            print(f"❌ Could not find weather channel {config.WEATHER_CHANNEL_ID}")
            return
        
        embeds = []
        
        # Loop through each location and collect weather embeds
        for location in self.scheduled_locations:
            print(f"Processing weather for: {location}")
            try:
                print(f"Fetching weather data for {location}...")
                data = await self.fetch_weather(location)
                if data:
                    print(f"Creating embed for {location}...")
                    embed = self.create_weather_embed(data, location)
                    embeds.append(embed)
                else:
                    print(f"❌ Failed to fetch weather data for {location}")
            except Exception as e:
                print(f"❌ Error processing weather for {location}: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
            
            # Add a small delay between requests to avoid rate limiting
            await asyncio.sleep(1)
            
        if embeds:
            print(f"Sending {len(embeds)} weather embeds...")
            try:
                await channel.send("Good morning! Here is the daily weather report:", embeds=embeds)
                print("✅ Successfully posted daily weather report")
            except Exception as e:
                print(f"❌ Error sending bulk weather message: {e}")
                print("⚠️ Falling back to sending individual messages...")
                for i, embed in enumerate(embeds):
                    try:
                        await channel.send(f"Weather for **{self.scheduled_locations[i]}**:", embed=embed)
                        await asyncio.sleep(1)
                    except Exception as inner_e:
                        print(f"❌ Failed to send individual embed: {inner_e}")
        else:
            print("❌ No weather data collected to post")

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
