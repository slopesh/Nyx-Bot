import discord
from discord.ext import commands
import pymongo
from datetime import datetime
from dotenv import load_dotenv
import os
import random

load_dotenv()

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = pymongo.MongoClient(os.getenv('MONGO_URI'))
        self.db = self.mongo_client['minecraft_proxy']
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
        
        # Default welcome messages
        self.welcome_messages = [
            "Welcome {username} to the server! 🎮",
            "Hey {username}, glad to have you here! 🎯",
            "Welcome aboard {username}! 🚀",
            "New user alert! Welcome {username}! 🎉",
            "Hey {username}, ready to play? 🎲"
        ]

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Check if user exists in database
        user = self.db.users.find_one({"username": member.name})
        if not user:
            return
            
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return
            
        # Get custom welcome message if exists
        welcome_msg = user.get('welcome_message')
        if not welcome_msg:
            welcome_msg = random.choice(self.welcome_messages)
            
        # Replace placeholders
        welcome_msg = welcome_msg.format(
            username=member.mention,
            server=member.guild.name
        )
        
        embed = discord.Embed(
            title="Welcome!",
            description=welcome_msg,
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        # Add user info
        embed.add_field(name="Username", value=user.get('username', 'N/A'), inline=True)
        embed.add_field(name="License Type", value=user.get('license_type', 'N/A'), inline=True)
        embed.add_field(name="Expiry Date", value=user.get('expiry_date', 'N/A'), inline=True)
        
        # Add avatar
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
            
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, username: str, *, message: str):
        """Set a custom welcome message for a user"""
        result = self.db.users.update_one(
            {"username": username},
            {"$set": {"welcome_message": message}}
        )
        
        if result.modified_count > 0:
            await ctx.send(f"✅ Welcome message set for {username}")
        else:
            await ctx.send(f"❌ User {username} not found")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resetwelcome(self, ctx, username: str):
        """Reset welcome message to default for a user"""
        result = self.db.users.update_one(
            {"username": username},
            {"$unset": {"welcome_message": ""}}
        )
        
        if result.modified_count > 0:
            await ctx.send(f"✅ Welcome message reset for {username}")
        else:
            await ctx.send(f"❌ User {username} not found")

async def setup(bot):
    await bot.add_cog(Welcome(bot)) 