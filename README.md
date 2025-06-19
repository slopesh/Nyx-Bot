# Minecraft Proxy Discord Bot

A Discord bot for monitoring and managing a Minecraft proxy client. The bot provides real-time alerts, user management, and security monitoring features with slash command support for Discord badges.

## Features

- Real-time user registration notifications
- Site uptime monitoring
- VPN and suspicious login detection
- License expiry notifications
- Account leak detection
- Log analysis and summarization
- Administrative commands
- User activity tracking
- Server status monitoring
- Custom welcome messages
- **Slash Commands** for Discord badge requirements
- **AutoMod Integration** for enhanced moderation
- **Rich Presence** and dynamic status updates

## Discord Badges

This bot is configured to earn the following Discord badges:
- 🛡️ **Uses AutoMod** - AutoMod integration for content filtering
- 🔧 **Supports Commands** - Slash command support
- 🤖 **Bot** - Standard bot badge


## Commands

### Slash Commands (Recommended)
- `/ping` - Check bot latency
- `/uptime` - Check bot uptime
- `/info` - Get bot information
- `/help` - Show available commands
- `/status` - Check server status
- `/register` - Register your Minecraft account
- `/check` - Check VPN/Proxy status
- `/activity` - View activity statistics
- `/automod` - Manage AutoMod rules (Admin only)
- `/db_stats` - Show database statistics (Admin only)
- `/ban` - Ban a user (Admin only)

### Prefix Commands (Legacy)
- `!ping` - Check bot latency
- `!db-stats` - Show database statistics
- `!ban <username> [reason]` - Ban a user
- `!info [username]` - Get user information
- `!analyze-logs [hours]` - Analyze logs from the last X hours
- `!activity [username]` - Get user activity statistics
- `!status` - Get detailed server status
- `!setwelcome <username> <message>` - Set custom welcome message
- `!resetwelcome <username>` - Reset welcome message to default

## Handlers

- `registration.py` - Sends embed when new users register
- `monitor.py` - Monitors site uptime
- `geoip_vpn_check.py` - Checks for VPN usage and suspicious logins
- `expiry_notifier.py` - Sends license expiry reminders
- `leak_detector.py` - Detects account sharing/leaks
- `log_ai_parser.py` - Analyzes and summarizes logs
- `commands.py` - Basic bot commands with slash command support
- `activity_tracker.py` - Tracks user activity and sends alerts
- `server_status.py` - Monitors server resources and performance
- `welcome.py` - Handles custom welcome messages
- `automod_integration.py` - AutoMod integration for badges


## Health Check Endpoints

The bot provides several health check endpoints:
- `/` - Basic status
- `/health` - Detailed health information
- `/metrics` - System metrics
- `/status` - Bot status
- `/ping` - Simple ping


## License

MIT License 
