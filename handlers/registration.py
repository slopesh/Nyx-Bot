import discord
from discord.ext import commands
import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = pymongo.MongoClient(os.getenv('MONGO_URI'))
        self.db = self.mongo_client['minecraft_proxy']
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
        
        # Set up change stream for new user documents
        self.change_stream = self.db.users.watch(
            [{'$match': {'operationType': 'insert'}}]
        )
        self.bot.loop.create_task(self.watch_registrations())

    async def watch_registrations(self):
        while True:
            try:
                change = self.change_stream.next()
                if change['operationType'] == 'insert':
                    await self.send_registration_alert(change['fullDocument'])
            except Exception as e:
                print(f"Error in registration watcher: {e}")
                continue

    async def send_registration_alert(self, user_doc):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        embed = discord.Embed(
            title="New User Registration",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Username", value=user_doc.get('username', 'N/A'), inline=True)
        embed.add_field(name="Email", value=user_doc.get('email', 'N/A'), inline=True)
        embed.add_field(name="License Type", value=user_doc.get('license_type', 'N/A'), inline=True)
        embed.add_field(name="Expiry Date", value=user_doc.get('expiry_date', 'N/A'), inline=True)
        
        if 'ip_address' in user_doc:
            embed.add_field(name="IP Address", value=user_doc['ip_address'], inline=True)
        if 'country' in user_doc:
            embed.add_field(name="Country", value=user_doc['country'], inline=True)
            
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Registration(bot)) 