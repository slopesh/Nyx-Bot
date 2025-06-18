import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger('automod')

class AutoModIntegration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("AutoModIntegration cog ready.")
        await self.setup_automod_rules()

    async def setup_automod_rules(self):
        """Set up AutoMod rules for badge requirements"""
        for guild in self.bot.guilds:
            try:
                if not guild.me.guild_permissions.manage_guild:
                    logger.warning(f"Bot lacks 'Manage Guild' permissions in {guild.name}")
                    continue
                
                # Check if AutoMod rules already exist
                existing_rules = await guild.fetch_automod_rules()
                if existing_rules:
                    logger.info(f"AutoMod rules already exist in {guild.name}")
                    continue
                
                # Create basic AutoMod rule for badge requirements
                await self.create_basic_automod_rule(guild)
                
            except Exception as e:
                logger.error(f"Error setting up AutoMod in {guild.name}: {e}")

    async def create_basic_automod_rule(self, guild):
        """Create a basic AutoMod rule for badge requirements"""
        try:
            # Find a suitable channel for alerts (first text channel with send permissions)
            alert_channel = None
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    alert_channel = channel
                    break
            
            if not alert_channel:
                logger.warning(f"No suitable alert channel found in {guild.name}")
                return
            
            # Create AutoMod rule
            rule = await guild.create_automod_rule(
                trigger_type=discord.AutoModTriggerType.keyword,
                trigger_metadata=discord.AutoModTriggerMetadata(
                    keyword_filter=["spam", "scam", "inappropriate"]
                ),
                actions=[
                    discord.AutoModBlockMessageAction(reason="AutoMod: Inappropriate content"),
                    discord.AutoModSendAlertAction(channel=alert_channel)
                ],
                name="Basic Content Filter",
                enabled=True
            )
            logger.info(f"Created AutoMod rule '{rule.name}' in {guild.name}")
            
        except discord.Forbidden:
            logger.error(f"Bot lacks permissions to create AutoMod rules in {guild.name}")
        except Exception as e:
            logger.error(f"Error creating AutoMod rule in {guild.name}: {e}")

    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModActionExecution):
        """Handle AutoMod actions"""
        logger.info(f"AutoMod action detected in {execution.guild.name}: "
                   f"Rule: {execution.rule_trigger_type.name} - "
                   f"Content: {execution.content[:50]}...")
        
        # Send detailed log to a designated channel if available
        await self.log_automod_action(execution)

    async def log_automod_action(self, execution):
        """Log AutoMod actions to a designated channel"""
        try:
            # Find a log channel (you can customize this)
            log_channel = None
            for channel in execution.guild.text_channels:
                if "log" in channel.name.lower() or "mod" in channel.name.lower():
                    if channel.permissions_for(execution.guild.me).send_messages:
                        log_channel = channel
                        break
            
            if not log_channel:
                return
            
            embed = discord.Embed(
                title="🛡️ AutoMod Action",
                description=f"**Rule:** {execution.rule_trigger_type.name}\n"
                           f"**Channel:** {execution.channel.mention}\n"
                           f"**User:** {execution.member.mention if execution.member else 'Unknown'}",
                color=0xff6b6b
            )
            embed.add_field(name="Content", value=f"```{execution.content[:1000]}```", inline=False)
            embed.add_field(name="Action", value=execution.action.type.name, inline=True)
            embed.set_footer(text=f"User ID: {execution.member.id if execution.member else 'Unknown'}")
            embed.timestamp = discord.utils.utcnow()
            
            await log_channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error logging AutoMod action: {e}")

    # Slash commands for AutoMod management
    @app_commands.command(name="automod", description="Manage AutoMod rules")
    @app_commands.describe(
        action="Action to perform",
        rule_name="Name of the rule (for delete action)"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="list", value="list"),
        app_commands.Choice(name="create", value="create"),
        app_commands.Choice(name="delete", value="delete")
    ])
    async def automod_command(self, interaction: discord.Interaction, action: str, rule_name: str = None):
        """Manage AutoMod rules"""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
        
        if not interaction.guild.me.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ I need 'Manage Guild' permissions to manage AutoMod rules.", ephemeral=True)
            return
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need 'Manage Guild' permissions to use this command.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            if action == "list":
                await self.list_automod_rules(interaction)
            elif action == "create":
                await self.create_automod_rule_interactive(interaction)
            elif action == "delete":
                if not rule_name:
                    await interaction.followup.send("❌ Please provide a rule name to delete.", ephemeral=True)
                    return
                await self.delete_automod_rule(interaction, rule_name)
        except Exception as e:
            logger.error(f"Error in automod command: {e}")
            await interaction.followup.send(f"❌ An error occurred: {e}", ephemeral=True)

    async def list_automod_rules(self, interaction: discord.Interaction):
        """List all AutoMod rules"""
        try:
            rules = await interaction.guild.fetch_automod_rules()
            
            if not rules:
                embed = discord.Embed(
                    title="🛡️ AutoMod Rules",
                    description="No AutoMod rules found in this server.",
                    color=0x0099ff
                )
            else:
                embed = discord.Embed(
                    title="🛡️ AutoMod Rules",
                    description=f"Found {len(rules)} AutoMod rule(s):",
                    color=0x0099ff
                )
                
                for rule in rules:
                    status = "✅ Enabled" if rule.enabled else "❌ Disabled"
                    embed.add_field(
                        name=f"{rule.name} ({status})",
                        value=f"**Type:** {rule.trigger_type.name}\n**Actions:** {len(rule.actions)}",
                        inline=True
                    )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error listing rules: {e}", ephemeral=True)

    async def create_automod_rule_interactive(self, interaction: discord.Interaction):
        """Create a new AutoMod rule interactively"""
        try:
            # Create a basic rule
            rule = await interaction.guild.create_automod_rule(
                trigger_type=discord.AutoModTriggerType.keyword,
                trigger_metadata=discord.AutoModTriggerMetadata(
                    keyword_filter=["spam", "inappropriate"]
                ),
                actions=[
                    discord.AutoModBlockMessageAction(reason="AutoMod: Basic filter")
                ],
                name="Basic Filter",
                enabled=True
            )
            
            embed = discord.Embed(
                title="✅ AutoMod Rule Created",
                description=f"Successfully created rule: **{rule.name}**",
                color=0x00ff00
            )
            embed.add_field(name="Type", value=rule.trigger_type.name, inline=True)
            embed.add_field(name="Status", value="Enabled" if rule.enabled else "Disabled", inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error creating rule: {e}", ephemeral=True)

    async def delete_automod_rule(self, interaction: discord.Interaction, rule_name: str):
        """Delete an AutoMod rule"""
        try:
            rules = await interaction.guild.fetch_automod_rules()
            rule_to_delete = None
            
            for rule in rules:
                if rule.name.lower() == rule_name.lower():
                    rule_to_delete = rule
                    break
            
            if not rule_to_delete:
                await interaction.followup.send(f"❌ No rule found with name: {rule_name}", ephemeral=True)
                return
            
            await rule_to_delete.delete()
            
            embed = discord.Embed(
                title="✅ AutoMod Rule Deleted",
                description=f"Successfully deleted rule: **{rule_to_delete.name}**",
                color=0x00ff00
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error deleting rule: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutoModIntegration(bot)) 