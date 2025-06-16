import discord
from discord.ext import commands
from datetime import datetime
import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = pymongo.MongoClient(os.getenv('MONGO_URI'))
        self.db = self.mongo_client['minecraft_proxy']

    @commands.command()
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(title="Ping Pong!", description=f'🏓 Pong! Latency: {latency}ms', color=0x7289DA)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def db_stats(self, ctx):
        """Show database statistics"""
        users = self.db.users.count_documents({})
        active = self.db.users.count_documents({"status": "active"})
        banned = self.db.users.count_documents({"status": "banned"})
        
        embed = discord.Embed(title="Database Statistics", color=0x7289DA)
        embed.add_field(name="Total Users", value=users, inline=True)
        embed.add_field(name="Active Users", value=active, inline=True)
        embed.add_field(name="Banned Users", value=banned, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, username: str, *, reason: str = "No reason provided"):
        """Ban a user from the proxy"""
        result = self.db.users.update_one(
            {"username": username},
            {"$set": {"status": "banned", "ban_reason": reason, "banned_at": datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            await ctx.send(f"✅ Successfully banned {username}")
        else:
            await ctx.send(f"❌ User {username} not found")

    @commands.command()
    async def info(self, ctx, username: str = None):
        """Get information about a user or yourself"""
        if username is None:
            username = ctx.author.name
            
        user = self.db.users.find_one({"username": username})
        if not user:
            await ctx.send(f"❌ User {username} not found")
            return
            
        embed = discord.Embed(title=f"User Info: {username}", color=discord.Color.green())
        embed.add_field(name="Status", value=user.get("status", "unknown"), inline=True)
        embed.add_field(name="License Expiry", value=user.get("expiry_date", "N/A"), inline=True)
        embed.add_field(name="Last Login", value=user.get("last_login", "Never"), inline=True)
        
        if user.get("status") == "banned":
            embed.add_field(name="Ban Reason", value=user.get("ban_reason", "No reason provided"), inline=False)
            
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Commands(bot)) 