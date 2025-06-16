import discord
from discord.ext import commands
import pymongo
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

class ActivityTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = pymongo.MongoClient(os.getenv('MONGO_URI'))
        self.db = self.mongo_client['minecraft_proxy']
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
        self.bot.loop.create_task(self.track_activity())

    async def track_activity(self):
        while True:
            try:
                # Get all active users
                active_users = self.db.users.find({"status": "active"})
                
                for user in active_users:
                    # Get last login time
                    last_login = user.get('last_login')
                    if not last_login:
                        continue
                        
                    # Check if user hasn't logged in for 7 days
                    if datetime.utcnow() - last_login > timedelta(days=7):
                        await self.send_inactivity_alert(user)
                        
                        # Update user status
                        self.db.users.update_one(
                            {"_id": user["_id"]},
                            {"$set": {"status": "inactive"}}
                        )
                
            except Exception as e:
                print(f"Error in activity tracker: {e}")
                
            await asyncio.sleep(3600)  # Check every hour

    async def send_inactivity_alert(self, user):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        embed = discord.Embed(
            title="💤 User Inactivity Alert",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Username", value=user.get('username', 'N/A'), inline=True)
        embed.add_field(name="Last Login", value=user['last_login'].strftime("%Y-%m-%d %H:%M UTC"), inline=True)
        embed.add_field(name="License Type", value=user.get('license_type', 'N/A'), inline=True)
        
        await channel.send(embed=embed)

    @commands.command()
    async def activity(self, ctx, username: str = None):
        """Get user activity statistics"""
        if username is None:
            username = ctx.author.name
            
        user = self.db.users.find_one({"username": username})
        if not user:
            await ctx.send(f"❌ User {username} not found")
            return
            
        # Get login history
        login_history = list(self.db.login_logs.find(
            {"username": username},
            sort=[("timestamp", -1)],
            limit=10
        ))
        
        embed = discord.Embed(
            title=f"Activity Stats: {username}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Add basic info
        embed.add_field(name="Status", value=user.get("status", "unknown"), inline=True)
        embed.add_field(name="Last Login", value=user.get("last_login", "Never"), inline=True)
        
        # Add login history
        if login_history:
            history_text = ""
            for login in login_history:
                timestamp = login.get('timestamp', datetime.utcnow())
                ip = login.get('ip_address', 'N/A')
                history_text += f"• {timestamp.strftime('%Y-%m-%d %H:%M')} - {ip}\n"
            embed.add_field(name="Recent Logins", value=history_text, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ActivityTracker(bot)) 