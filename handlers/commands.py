import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import pymongo
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger('commands')

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = None
        self.db = None
        self.setup_mongodb()

    def setup_mongodb(self):
        """Setup MongoDB connection with error handling"""
        try:
            mongo_uri = os.getenv('MONGO_URI')
            if not mongo_uri:
                logger.warning("MONGO_URI not found in environment variables")
                return
            
            self.mongo_client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.mongo_client.admin.command('ping')
            self.db = self.mongo_client['minecraft_proxy']
            logger.info("MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.mongo_client = None
            self.db = None

    def check_mongodb(self):
        """Check if MongoDB is available"""
        if not self.db:
            return False
        try:
            self.mongo_client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB connection lost: {e}")
            return False

    # Prefix commands (legacy support)
    @commands.command()
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!", 
            description=f'Latency: **{latency}ms**', 
            color=0x00ff00
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def db_stats(self, ctx):
        """Show database statistics"""
        if not self.check_mongodb():
            await ctx.send("❌ Database connection not available")
            return
        
        try:
            users = self.db.users.count_documents({})
            active = self.db.users.count_documents({"status": "active"})
            banned = self.db.users.count_documents({"status": "banned"})
            
            embed = discord.Embed(title="📊 Database Statistics", color=0x0099ff)
            embed.add_field(name="Total Users", value=users, inline=True)
            embed.add_field(name="Active Users", value=active, inline=True)
            embed.add_field(name="Banned Users", value=banned, inline=True)
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in db_stats command: {e}")
            await ctx.send("❌ Error fetching database statistics")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, username: str, *, reason: str = "No reason provided"):
        """Ban a user from the proxy"""
        if not self.check_mongodb():
            await ctx.send("❌ Database connection not available")
            return
        
        try:
            result = self.db.users.update_one(
                {"username": username},
                {"$set": {"status": "banned", "ban_reason": reason, "banned_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                embed = discord.Embed(
                    title="✅ User Banned",
                    description=f"Successfully banned **{username}**",
                    color=0xff6b6b
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.set_footer(text=f"Banned by {ctx.author.name}")
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ User **{username}** not found")
        except Exception as e:
            logger.error(f"Error in ban command: {e}")
            await ctx.send("❌ Error banning user")

    @commands.command()
    async def info(self, ctx, username: str = None):
        """Get information about a user or yourself"""
        if not self.check_mongodb():
            await ctx.send("❌ Database connection not available")
            return
        
        try:
            if username is None:
                username = ctx.author.name
                
            user = self.db.users.find_one({"username": username})
            if not user:
                await ctx.send(f"❌ User **{username}** not found")
                return
                
            embed = discord.Embed(title=f"👤 User Info: {username}", color=0x0099ff)
            embed.add_field(name="Status", value=user.get("status", "unknown"), inline=True)
            embed.add_field(name="License Expiry", value=user.get("expiry_date", "N/A"), inline=True)
            embed.add_field(name="Last Login", value=user.get("last_login", "Never"), inline=True)
            
            if user.get("status") == "banned":
                embed.add_field(name="Ban Reason", value=user.get("ban_reason", "No reason provided"), inline=False)
                
            embed.set_footer(text=f"Requested by {ctx.author.name}")
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in info command: {e}")
            await ctx.send("❌ Error fetching user information")

    # Slash commands for badge requirements
    @app_commands.command(name="ping", description="Check bot latency")
    async def slash_ping(self, interaction: discord.Interaction):
        """Slash command version of ping"""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!", 
            description=f'Latency: **{latency}ms**', 
            color=0x00ff00
        )
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="db_stats", description="Show database statistics (Admin only)")
    @app_commands.describe()
    async def slash_db_stats(self, interaction: discord.Interaction):
        """Slash command version of db_stats"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
            return
        
        if not self.check_mongodb():
            await interaction.response.send_message("❌ Database connection not available", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            users = self.db.users.count_documents({})
            active = self.db.users.count_documents({"status": "active"})
            banned = self.db.users.count_documents({"status": "banned"})
            
            embed = discord.Embed(title="📊 Database Statistics", color=0x0099ff)
            embed.add_field(name="Total Users", value=users, inline=True)
            embed.add_field(name="Active Users", value=active, inline=True)
            embed.add_field(name="Banned Users", value=banned, inline=True)
            embed.set_footer(text=f"Requested by {interaction.user.name}")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in slash db_stats command: {e}")
            await interaction.followup.send("❌ Error fetching database statistics", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a user from the proxy (Admin only)")
    @app_commands.describe(
        username="Username to ban",
        reason="Reason for the ban"
    )
    async def slash_ban(self, interaction: discord.Interaction, username: str, reason: str = "No reason provided"):
        """Slash command version of ban"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
            return
        
        if not self.check_mongodb():
            await interaction.response.send_message("❌ Database connection not available", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            result = self.db.users.update_one(
                {"username": username},
                {"$set": {"status": "banned", "ban_reason": reason, "banned_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                embed = discord.Embed(
                    title="✅ User Banned",
                    description=f"Successfully banned **{username}**",
                    color=0xff6b6b
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.set_footer(text=f"Banned by {interaction.user.name}")
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"❌ User **{username}** not found", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in slash ban command: {e}")
            await interaction.followup.send("❌ Error banning user", ephemeral=True)

    @app_commands.command(name="info", description="Get information about a user")
    @app_commands.describe(username="Username to look up (leave empty for yourself)")
    async def slash_info(self, interaction: discord.Interaction, username: str = None):
        """Slash command version of info"""
        if username is None:
            username = interaction.user.name
        
        if not self.check_mongodb():
            await interaction.response.send_message("❌ Database connection not available", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            user = self.db.users.find_one({"username": username})
            if not user:
                await interaction.followup.send(f"❌ User **{username}** not found", ephemeral=True)
                return
                
            embed = discord.Embed(title=f"👤 User Info: {username}", color=0x0099ff)
            embed.add_field(name="Status", value=user.get("status", "unknown"), inline=True)
            embed.add_field(name="License Expiry", value=user.get("expiry_date", "N/A"), inline=True)
            embed.add_field(name="Last Login", value=user.get("last_login", "Never"), inline=True)
            
            if user.get("status") == "banned":
                embed.add_field(name="Ban Reason", value=user.get("ban_reason", "No reason provided"), inline=False)
                
            embed.set_footer(text=f"Requested by {interaction.user.name}")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in slash info command: {e}")
            await interaction.followup.send("❌ Error fetching user information", ephemeral=True)

    @app_commands.command(name="status", description="Check proxy server status")
    async def slash_status(self, interaction: discord.Interaction):
        """Check proxy server status"""
        await interaction.response.defer()
        
        try:
            # This would typically check your actual proxy server
            # For now, we'll simulate a status check
            embed = discord.Embed(title="🟢 Proxy Status", color=0x00ff00)
            embed.add_field(name="Status", value="Online", inline=True)
            embed.add_field(name="Players", value="0/100", inline=True)
            embed.add_field(name="Uptime", value="99.9%", inline=True)
            embed.add_field(name="Server", value="proxy.example.com", inline=True)
            embed.add_field(name="Port", value="25565", inline=True)
            embed.set_footer(text=f"Requested by {interaction.user.name}")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in slash status command: {e}")
            await interaction.followup.send("❌ Error checking server status", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Commands(bot)) 