# Minecraft Proxy Discord Bot

A Discord bot for monitoring and managing a Minecraft proxy client. The bot provides real-time alerts, user management, and security monitoring features.

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

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   MONGO_URI=your_mongodb_connection_string
   WATCH_URL=your_minecraft_proxy_url
   DISCORD_CHANNEL_ID=your_discord_channel_id
   ```
4. Download the GeoLite2 Country database and place it in the root directory as `GeoLite2-Country.mmdb`
5. Run the bot:
   ```bash
   python bot.py
   ```

## Commands

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
- `commands.py` - Basic bot commands
- `activity_tracker.py` - Tracks user activity and sends alerts
- `server_status.py` - Monitors server resources and performance
- `welcome.py` - Handles custom welcome messages

## Replit Deployment

1. Create a new Replit project
2. Upload all files
3. Add environment variables in Replit's Secrets tab
4. Run the bot

The `keep_alive.py` script will keep the bot running 24/7 on Replit's free tier.

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- Regularly update dependencies for security patches
- Monitor the bot's logs for any suspicious activity
- Use strong MongoDB credentials and restrict database access

## License

MIT License 