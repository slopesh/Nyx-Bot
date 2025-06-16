import discord
from discord.ext import commands
import psutil
import platform
import time
from datetime import datetime
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

class ServerStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
        self.bot.loop.create_task(self.monitor_server())

    async def monitor_server(self):
        while True:
            try:
                # Get system stats
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Check if any metric exceeds threshold
                if cpu_percent > 80 or memory.percent > 80 or disk.percent > 80:
                    await self.send_alert(cpu_percent, memory.percent, disk.percent)
                
            except Exception as e:
                print(f"Error in server monitor: {e}")
                
            await asyncio.sleep(300)  # Check every 5 minutes

    async def send_alert(self, cpu_percent, memory_percent, disk_percent):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        embed = discord.Embed(
            title="⚠️ High Resource Usage Alert",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="CPU Usage", value=f"{cpu_percent}%", inline=True)
        embed.add_field(name="Memory Usage", value=f"{memory_percent}%", inline=True)
        embed.add_field(name="Disk Usage", value=f"{disk_percent}%", inline=True)
        
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def status(self, ctx):
        """Get detailed server status"""
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get uptime
        uptime = time.time() - psutil.boot_time()
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        
        embed = discord.Embed(
            title="Server Status",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # System info
        embed.add_field(name="OS", value=platform.system(), inline=True)
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Uptime", value=f"{days}d {hours}h {minutes}m", inline=True)
        
        # Resource usage
        embed.add_field(name="CPU Usage", value=f"{cpu_percent}%", inline=True)
        embed.add_field(name="Memory Usage", value=f"{memory.percent}% ({memory.used / 1024 / 1024 / 1024:.1f}GB / {memory.total / 1024 / 1024 / 1024:.1f}GB)", inline=True)
        embed.add_field(name="Disk Usage", value=f"{disk.percent}% ({disk.used / 1024 / 1024 / 1024:.1f}GB / {disk.total / 1024 / 1024 / 1024:.1f}GB)", inline=True)
        
        # Network info
        net_io = psutil.net_io_counters()
        embed.add_field(name="Network", value=f"↑ {net_io.bytes_sent / 1024 / 1024:.1f}MB\n↓ {net_io.bytes_recv / 1024 / 1024:.1f}MB", inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerStatus(bot)) 