import discord
from discord.ext import commands
import requests
import asyncio
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

class Monitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.watch_url = os.getenv('WATCH_URL')
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
        self.is_down = False
        self.bot.loop.create_task(self.monitor_site())

    async def monitor_site(self):
        while True:
            try:
                response = requests.get(self.watch_url, timeout=10)
                if response.status_code != 200 and not self.is_down:
                    await self.send_down_alert()
                    self.is_down = True
                elif response.status_code == 200 and self.is_down:
                    await self.send_up_alert()
                    self.is_down = False
            except requests.RequestException as e:
                if not self.is_down:
                    await self.send_down_alert()
                    self.is_down = True
            await asyncio.sleep(60)  # Check every minute

    async def send_down_alert(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        embed = discord.Embed(
            title="⚠️ Site Down Alert",
            description=f"The site at {self.watch_url} is currently down!",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        await channel.send(embed=embed)

    async def send_up_alert(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        embed = discord.Embed(
            title="✅ Site Back Online",
            description=f"The site at {self.watch_url} is now back online!",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Monitor(bot)) 