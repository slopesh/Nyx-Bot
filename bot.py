import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import keep_alive
import importlib
import glob
import logging
import sys
from datetime import datetime
import pathlib

# Configure logging for Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger('bot')

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class MinecraftProxyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        self.start_time = datetime.utcnow()
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Setting up bot...")
        
        # Load all extensions
        await self.load_extensions()
        
        # Sync slash commands
        logger.info("Syncing slash commands...")
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def load_extensions(self):
        """Load all Python files from the handlers directory"""
        for handler in glob.glob('handlers/*.py'):
            if handler.endswith('.py'):
                module_name = pathlib.Path(handler).with_suffix('').as_posix().replace('/', '.')
                try:
                    await self.load_extension(module_name)
                    logger.info(f"Loaded extension: {module_name}")
                except Exception as e:
                    logger.error(f"Failed to load extension {module_name}: {e}")

    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'Logged in as {self.user.name} ({self.user.id})')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        logger.info('------')
        
        # Set bot status dynamically
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"over {len(self.users)} users and proxy"
            )
        )
        
        # Set up AutoMod integration
        await self.setup_automod()
    
    async def setup_automod(self):
        """Set up AutoMod integration for badges"""
        try:
            for guild in self.guilds:
                if guild.me.guild_permissions.manage_guild:
                    # Enable AutoMod features
                    logger.info(f"Setting up AutoMod for guild: {guild.name}")
        except Exception as e:
            logger.error(f"Failed to setup AutoMod: {e}")

    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
            return
        
        # Log other errors
        logger.error(f"Error in command {ctx.command}: {error}", exc_info=True)
        await ctx.send("❌ An error occurred while processing the command.")

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handle slash command errors"""
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏰ This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
        else:
            logger.error(f"Error in slash command: {error}", exc_info=True)
            await interaction.response.send_message(
                "❌ An error occurred while processing the command.",
                ephemeral=True
            )

# Create bot instance
bot = MinecraftProxyBot()

# Global slash commands
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    """Ping command to check bot latency"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=0x00ff00
    )
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="uptime", description="Check bot uptime")
async def uptime(interaction: discord.Interaction):
    """Check bot uptime"""
    uptime_delta = datetime.utcnow() - bot.start_time
    days = uptime_delta.days
    hours, remainder = divmod(uptime_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    embed = discord.Embed(
        title="⏰ Bot Uptime",
        description=f"**{days}** days, **{hours}** hours, **{minutes}** minutes, **{seconds}** seconds",
        color=0x0099ff
    )
    embed.set_footer(text=f"Started at {bot.start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="Get bot information")
async def info(interaction: discord.Interaction):
    """Get bot information"""
    embed = discord.Embed(
        title="🤖 Bot Information",
        color=0x0099ff
    )
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Users", value=len(bot.users), inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Python Version", value=sys.version.split()[0], inline=True)
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    """Show help information"""
    embed = discord.Embed(
        title="📚 Bot Commands",
        description="Here are the available commands:",
        color=0x0099ff
    )
    
    # Slash commands
    embed.add_field(
        name="🔧 Slash Commands",
        value="""
        `/ping` - Check bot latency
        `/uptime` - Check bot uptime
        `/info` - Get bot information
        `/help` - Show this help message
        `/status` - Check server status
        `/register` - Register your Minecraft account
        `/check` - Check VPN/Proxy status
        `/activity` - View activity statistics
        """,
        inline=False
    )
    
    # Prefix commands (legacy)
    embed.add_field(
        name="⌨️ Prefix Commands",
        value="""
        `!ping` - Check bot latency
        `!status` - Check server status
        `!register` - Register your Minecraft account
        `!check` - Check VPN/Proxy status
        `!activity` - View activity statistics
        """,
        inline=False
    )
    
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

async def main():
    """Main function to run the bot"""
    try:
        # Start the keep_alive server for Render
        keep_alive.keep_alive()
        
        # Get Discord token
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.critical("DISCORD_TOKEN not found in environment variables!")
            sys.exit(1)
        
        # Start the bot
        async with bot:
            await bot.start(token)
    except Exception as e:
        logger.critical(f"Critical error in main: {e}", exc_info=True)
        raise

# Run the bot
if __name__ == "__main__":
    try:
        # Set up asyncio for Render
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1) 