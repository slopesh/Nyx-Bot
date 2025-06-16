import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import keep_alive
import importlib
import glob
import logging
import sys

# Configure logging
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

bot = commands.Bot(command_prefix='!', intents=intents)

async def load_extensions():
    # Load all Python files from the handlers directory
    for handler in glob.glob('handlers/*.py'):
        if handler.endswith('.py'):
            module_name = handler.replace('/', '.').replace('.py', '')
            try:
                await bot.load_extension(module_name)
                logger.info(f"Loaded extension: {module_name}")
            except Exception as e:
                logger.error(f"Failed to load extension {module_name}: {e}")

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} ({bot.user.id})')
    logger.info('------')
    
    # Set bot status dynamically
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"over {len(bot.users)} users and proxy"
        )
    )

@bot.event
async def on_command_error(ctx, error):
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

async def main():
    try:
        # Start the keep_alive server
        keep_alive.keep_alive()
        
        # Load all extensions
        await load_extensions()
        
        # Start the bot
        async with bot:
            await bot.start(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        logger.critical(f"Critical error in main: {e}", exc_info=True)
        raise

# Run the bot
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True) 