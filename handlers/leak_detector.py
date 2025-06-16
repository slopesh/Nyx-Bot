import discord
from discord.ext import commands
import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

class LeakDetector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = pymongo.MongoClient(os.getenv('MONGO_URI'))
        self.db = self.mongo_client['minecraft_proxy']
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
        
        # Set up change stream for login events
        self.change_stream = self.db.login_logs.watch(
            [{'$match': {'operationType': 'insert'}}]
        )
        self.bot.loop.create_task(self.watch_logins())

    async def watch_logins(self):
        while True:
            try:
                change = self.change_stream.next()
                if change['operationType'] == 'insert':
                    await self.check_for_leaks(change['fullDocument'])
            except Exception as e:
                print(f"Error in leak detector: {e}")
                continue

    async def check_for_leaks(self, login_doc):
        username = login_doc.get('username')
        hwid = login_doc.get('hwid')
        ip = login_doc.get('ip_address')

        if not username or not hwid or not ip:
            return

        # Check for multiple HWIDs
        hwid_count = self.db.login_logs.count_documents({
            "username": username,
            "hwid": {"$ne": hwid}
        })

        # Check for multiple IPs in last 24 hours
        recent_logins = self.db.login_logs.find({
            "username": username,
            "timestamp": {"$gte": datetime.utcnow() - timedelta(hours=24)},
            "ip_address": {"$ne": ip}
        })

        unique_ips = set()
        for login in recent_logins:
            unique_ips.add(login['ip_address'])

        if hwid_count > 0 or len(unique_ips) > 1:
            await self.send_leak_alert(username, hwid, ip, hwid_count, len(unique_ips))

    async def send_leak_alert(self, username, hwid, ip, hwid_count, ip_count):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        embed = discord.Embed(
            title="🚨 Possible Account Leak Detected",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="Current HWID", value=hwid, inline=True)
        embed.add_field(name="Current IP", value=ip, inline=True)
        
        reasons = []
        if hwid_count > 0:
            reasons.append(f"Multiple HWIDs detected ({hwid_count + 1} total)")
        if ip_count > 1:
            reasons.append(f"Multiple IPs in last 24 hours ({ip_count} total)")
            
        embed.add_field(name="Alert Reasons", value="\n".join(reasons), inline=False)
        
        # Get all known HWIDs and IPs
        all_logins = self.db.login_logs.find({"username": username})
        known_hwids = set()
        known_ips = set()
        
        for login in all_logins:
            if login.get('hwid'):
                known_hwids.add(login['hwid'])
            if login.get('ip_address'):
                known_ips.add(login['ip_address'])
        
        if known_hwids:
            embed.add_field(name="Known HWIDs", value="\n".join(known_hwids), inline=False)
        if known_ips:
            embed.add_field(name="Known IPs", value="\n".join(known_ips), inline=False)
        
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LeakDetector(bot)) 