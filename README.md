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

## Render Deployment (Recommended)

1. **Fork/Clone** this repository to your GitHub account
2. **Sign up** for [Render](https://render.com) (free tier available)
3. **Create a new Web Service**:
   - Connect your GitHub repository
   - Choose **Python** as the environment
   - Set **Build Command**: `pip install -r requirements.txt`
   - Set **Start Command**: `python bot.py`
   - Choose **Free** plan
4. **Add Environment Variables**:
   - `DISCORD_TOKEN` - Your Discord bot token
   - `MONGO_URI` - Your MongoDB connection string
   - `WATCH_URL` - Your Minecraft proxy URL
   - `DISCORD_CHANNEL_ID` - Your Discord channel ID
5. **Deploy** - Render will automatically deploy your bot

The bot includes a Flask-based keep-alive server that runs on the port provided by Render's `PORT` environment variable.

### Render Configuration

The `render.yaml` file is included for easy deployment:
```yaml
services:
  - type: web
    name: minecraft-proxy-bot
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python bot.py
    envVars:
      - key: DISCORD_TOKEN
        sync: false
      - key: MONGO_URI
        sync: false
      - key: ENVIRONMENT
        value: production
    healthCheckPath: /health
    autoDeploy: true
```

## Replit Deployment (Alternative)

1. Create a new Replit project
2. Upload all files
3. Add environment variables in Replit's Secrets tab
4. Run the bot

The `keep_alive.py` script will keep the bot running 24/7 on Replit's free tier.

## Health Check Endpoints

The bot provides several health check endpoints:
- `/` - Basic status
- `/health` - Detailed health information
- `/metrics` - System metrics
- `/status` - Bot status
- `/ping` - Simple ping

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- Regularly update dependencies for security patches
- Monitor the bot's logs for any suspicious activity
- Use strong MongoDB credentials and restrict database access
- The bot requires "Manage Guild" permissions for AutoMod features

## Dependencies

All required dependencies are listed in `requirements.txt`:
- `discord.py==2.3.2` - Discord bot library with slash command support
- `python-dotenv==1.0.0` - Environment variable management
- `pymongo==4.6.1` - MongoDB driver
- `flask==3.0.0` - Web framework for keep-alive server
- `gunicorn==21.2.0` - WSGI server for production
- And more...

## License

MIT License 