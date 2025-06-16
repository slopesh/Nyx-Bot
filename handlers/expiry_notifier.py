import discord
from discord.ext import commands
import pymongo
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

class ExpiryNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = pymongo.MongoClient(os.getenv('MONGO_URI'))
        self.db = self.mongo_client['minecraft_proxy']
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
        self.bot.loop.create_task(self.check_expiries())

    async def check_expiries(self):
        while True:
            try:
                # Check for expiries in the next 7 days
                seven_days_from_now = datetime.utcnow() + timedelta(days=7)
                expiring_users = self.db.users.find({
                    "expiry_date": {
                        "$lte": seven_days_from_now,
                        "$gt": datetime.utcnow()
                    }
                })

                for user in expiring_users:
                    days_remaining = (user['expiry_date'] - datetime.utcnow()).days
                    if days_remaining in [1, 3, 7]:  # Notify at 7, 3, and 1 days before expiry
                        await self.send_expiry_notification(user, days_remaining)

                # Check for expired users
                expired_users = self.db.users.find({
                    "expiry_date": {"$lte": datetime.utcnow()},
                    "status": "active"
                })

                for user in expired_users:
                    await self.send_expired_notification(user)
                    # Update user status to expired
                    self.db.users.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"status": "expired"}}
                    )

            except Exception as e:
                print(f"Error in expiry checker: {e}")

            await asyncio.sleep(3600)  # Check every hour

    async def send_expiry_notification(self, user, days_remaining):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        embed = discord.Embed(
            title="⚠️ License Expiring Soon",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Username", value=user.get('username', 'N/A'), inline=True)
        embed.add_field(name="Days Remaining", value=str(days_remaining), inline=True)
        embed.add_field(name="Expiry Date", value=user['expiry_date'].strftime("%Y-%m-%d %H:%M UTC"), inline=True)
        embed.add_field(name="License Type", value=user.get('license_type', 'N/A'), inline=True)
        
        await channel.send(embed=embed)

    async def send_expired_notification(self, user):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        embed = discord.Embed(
            title="❌ License Expired",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Username", value=user.get('username', 'N/A'), inline=True)
        embed.add_field(name="Expiry Date", value=user['expiry_date'].strftime("%Y-%m-%d %H:%M UTC"), inline=True)
        embed.add_field(name="License Type", value=user.get('license_type', 'N/A'), inline=True)
        
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ExpiryNotifier(bot)) 