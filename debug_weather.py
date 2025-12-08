import aiohttp
import asyncio
import json

async def fetch_weather(location):
    url = f"https://wttr.in/{location}?format=j1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                print(json.dumps(data, indent=2))
            else:
                print("Failed")

asyncio.run(fetch_weather("Plano,Texas"))
