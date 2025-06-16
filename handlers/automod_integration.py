import discord
from discord.ext import commands

class AutoModIntegration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("AutoModIntegration cog ready.")
        # Example: Create a simple AutoMod rule when the bot starts
        # NOTE: Bot must have 'Manage Guild' permissions.
        # This is just an example, be careful with creating rules repeatedly.
        await self.create_example_automod_rule()

    async def create_example_automod_rule(self):
        for guild in self.bot.guilds:
            try:
                # This rule blocks messages containing specific keywords
                # You can customize keywords, actions, and trigger types.
                rule = await guild.create_automod_rule(
                    trigger_type=discord.AutoModTriggerType.keyword,
                    trigger_metadata=discord.AutoModTriggerMetadata(keywords=["badword", "anotherbadword"]),
                    actions=[
                        discord.AutoModBlockMessageAction(reason="Blocked by AutoMod integration"),
                        discord.AutoModSendAlertAction(channel=discord.Object(id=1384010013177155584)) # Your mod channel ID
                    ],
                    name="Block Profanity Example",
                    enabled=True
                )
                print(f"Created AutoMod rule '{rule.name}' in {guild.name}")
            except discord.Forbidden:
                print(f"Bot lacks permissions to manage AutoMod rules in {guild.name}")
            except Exception as e:
                print(f"Error creating AutoMod rule in {guild.name}: {e}")

    # You can also listen for AutoMod actions
    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModActionExecution):
        # Log or react to AutoMod actions
        print(f"AutoMod action detected! "
              f"Rule: {execution.rule_trigger_type.name} - "
              f"Content: {execution.content}")
        # You can send a message to a log channel here if you want

async def setup(bot):
    await bot.add_cog(AutoModIntegration(bot)) 