import discord
from discord.ext import commands
import pymongo
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import re
from collections import defaultdict

load_dotenv()

class LogAIParser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = pymongo.MongoClient(os.getenv('MONGO_URI'))
        self.db = self.mongo_client['minecraft_proxy']
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
        
        # Set up change stream for log events
        self.change_stream = self.db.logs.watch(
            [{'$match': {'operationType': 'insert'}}]
        )
        self.bot.loop.create_task(self.watch_logs())

    async def watch_logs(self):
        while True:
            try:
                change = self.change_stream.next()
                if change['operationType'] == 'insert':
                    await self.analyze_log(change['fullDocument'])
            except Exception as e:
                print(f"Error in log parser: {e}")
                continue

    async def analyze_log(self, log_doc):
        log_content = log_doc.get('content', '')
        if not log_content:
            return

        # Analyze log patterns
        patterns = {
            'errors': r'(?i)(error|exception|failed|crash)',
            'warnings': r'(?i)(warning|warn)',
            'connections': r'(?i)(connect|disconnect|join|leave)',
            'security': r'(?i)(hack|cheat|exploit|inject)',
            'performance': r'(?i)(lag|timeout|slow|performance)'
        }

        findings = defaultdict(list)
        for category, pattern in patterns.items():
            matches = re.finditer(pattern, log_content)
            for match in matches:
                # Get some context around the match
                start = max(0, match.start() - 50)
                end = min(len(log_content), match.end() + 50)
                context = log_content[start:end].strip()
                findings[category].append(context)

        if any(findings.values()):
            await self.send_log_summary(log_doc, findings)

    async def send_log_summary(self, log_doc, findings):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        embed = discord.Embed(
            title="📊 Log Analysis Summary",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )

        # Add basic log info
        embed.add_field(
            name="Log Info",
            value=f"Source: {log_doc.get('source', 'Unknown')}\n"
                  f"Timestamp: {log_doc.get('timestamp', 'Unknown')}",
            inline=False
        )

        # Add findings for each category
        for category, contexts in findings.items():
            if contexts:
                # Limit to 3 examples per category
                examples = contexts[:3]
                value = "\n\n".join([f"• {ctx}" for ctx in examples])
                if len(contexts) > 3:
                    value += f"\n\n... and {len(contexts) - 3} more"
                embed.add_field(
                    name=f"{category.title()} ({len(contexts)})",
                    value=value,
                    inline=False
                )

        # Add severity assessment
        severity = "Low"
        if len(findings['errors']) > 0:
            severity = "High"
        elif len(findings['warnings']) > 0:
            severity = "Medium"

        embed.add_field(
            name="Severity Assessment",
            value=f"Overall Severity: {severity}",
            inline=False
        )

        await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def analyze_logs(self, ctx, hours: int = 24):
        """Analyze logs from the last X hours"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        logs = self.db.logs.find({
            "timestamp": {"$gte": start_time}
        })

        # Collect statistics
        stats = defaultdict(int)
        error_patterns = defaultdict(int)
        
        for log in logs:
            content = log.get('content', '')
            if not content:
                continue

            # Count log types
            if re.search(r'(?i)error|exception', content):
                stats['errors'] += 1
            elif re.search(r'(?i)warning', content):
                stats['warnings'] += 1
            elif re.search(r'(?i)connect|disconnect', content):
                stats['connections'] += 1

            # Analyze error patterns
            for pattern in ['timeout', 'crash', 'failed', 'invalid']:
                if re.search(pattern, content, re.I):
                    error_patterns[pattern] += 1

        # Create summary embed
        embed = discord.Embed(
            title=f"📊 Log Analysis (Last {hours} hours)",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )

        # Add basic stats
        for category, count in stats.items():
            embed.add_field(name=category.title(), value=str(count), inline=True)

        # Add error patterns
        if error_patterns:
            error_summary = "\n".join([f"• {pattern}: {count}" for pattern, count in error_patterns.items()])
            embed.add_field(name="Common Error Patterns", value=error_summary, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LogAIParser(bot)) 