import discord
from discord.ext import commands
import pymongo
import geoip2.database
import requests
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

class GeoIPVPNCheck(commands.Cog):
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
                    await self.check_login(change['fullDocument'])
            except Exception as e:
                print(f"Error in login watcher: {e}")
                continue

    async def check_login(self, login_doc):
        ip = login_doc.get('ip_address')
        hwid = login_doc.get('hwid')
        username = login_doc.get('username')

        if not ip or not hwid:
            return

        # Check if IP is from a VPN/proxy
        is_vpn = await self.check_vpn(ip)
        
        # Get country from IP
        country = await self.get_country(ip)
        
        # Check for suspicious patterns
        suspicious = await self.check_suspicious_patterns(username, ip, hwid, country)
        
        if is_vpn or suspicious:
            await self.send_alert(username, ip, country, hwid, is_vpn, suspicious)

    async def check_vpn(self, ip):
        try:
            response = requests.get(f"https://proxycheck.io/v2/{ip}?key=YOUR_API_KEY&vpn=1")
            data = response.json()
            return data.get(ip, {}).get('proxy', 'no') == 'yes'
        except:
            return False

    async def get_country(self, ip):
        try:
            with geoip2.database.Reader('GeoLite2-Country.mmdb') as reader:
                response = reader.country(ip)
                return response.country.name
        except:
            return "Unknown"

    async def check_suspicious_patterns(self, username, ip, hwid, country):
        # Check for multiple IPs from different countries
        user_logins = self.db.login_logs.find({"username": username})
        countries = set()
        for login in user_logins:
            if login.get('country'):
                countries.add(login['country'])
        
        if len(countries) > 2:  # More than 2 different countries
            return True
            
        # Check for multiple HWIDs
        hwid_count = self.db.login_logs.count_documents({
            "username": username,
            "hwid": {"$ne": hwid}
        })
        
        return hwid_count > 0

    async def send_alert(self, username, ip, country, hwid, is_vpn, suspicious):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        embed = discord.Embed(
            title="⚠️ Suspicious Login Detected",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="IP Address", value=ip, inline=True)
        embed.add_field(name="Country", value=country, inline=True)
        embed.add_field(name="HWID", value=hwid, inline=True)
        
        reasons = []
        if is_vpn:
            reasons.append("VPN/Proxy detected")
        if suspicious:
            reasons.append("Suspicious login pattern")
            
        embed.add_field(name="Alert Reasons", value="\n".join(reasons), inline=False)
        
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GeoIPVPNCheck(bot)) 