# 🚀 Render Deployment Guide

## Prerequisites

1. **GitHub Repository** - Your bot code must be in a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com) (free tier available)
3. **Discord Bot Token** - From [Discord Developer Portal](https://discord.com/developers/applications)
4. **MongoDB Database** - MongoDB Atlas (free tier available)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository has these files:
- `bot.py` - Main bot file
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification
- `render.yaml` - Render configuration (optional)
- `Procfile` - Alternative to render.yaml
- `build.sh` - Build script
- `handlers/` - All handler files
- `keep_alive.py` - Flask server for keep-alive

### 2. Create Render Web Service

1. **Login to Render** and click "New +"
2. **Select "Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**

#### Basic Configuration:
- **Name**: `minecraft-proxy-bot` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to you
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (if bot is in root)
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command**: `python bot.py`
- **Plan**: `Free`

#### Advanced Configuration (Optional):
- **Health Check Path**: `/health`
- **Auto-Deploy**: Enable
- **Number of Instances**: 1

### 3. Environment Variables

Add these environment variables in Render dashboard:

#### Required Variables:
```
DISCORD_TOKEN=your_discord_bot_token_here
MONGO_URI=your_mongodb_connection_string_here
WATCH_URL=your_minecraft_proxy_url_here
DISCORD_CHANNEL_ID=your_discord_channel_id_here
```

#### Optional Variables:
```
ENVIRONMENT=production
PYTHONUNBUFFERED=1
```

### 4. Deploy

1. **Click "Create Web Service"**
2. **Wait for build to complete** (usually 2-5 minutes)
3. **Check logs** for any errors
4. **Test the bot** in Discord

## Render-Specific Requirements

### Python Version
- Specified in `runtime.txt`: `python-3.11.7`
- Render supports Python 3.7+

### Port Configuration
- Render automatically sets `PORT` environment variable
- Bot uses `os.environ.get('PORT', 8080)` to get the port
- Flask server binds to `0.0.0.0:PORT`

### Health Checks
- Bot provides `/health` endpoint for Render health checks
- Returns JSON with bot status and system metrics

### Build Process
- Render runs `pip install --upgrade pip && pip install -r requirements.txt`
- All dependencies are installed from `requirements.txt`
- Build fails if any dependency installation fails

## Troubleshooting

### Build Failures

#### Common Issues:
1. **Missing dependencies** - Check `requirements.txt`
2. **Python version mismatch** - Check `runtime.txt`
3. **Import errors** - Check all handler files

#### Solutions:
1. **Check build logs** in Render dashboard
2. **Test locally** with `pip install -r requirements.txt`
3. **Update dependencies** if needed

### Runtime Errors

#### Common Issues:
1. **Missing environment variables** - Check all required vars are set
2. **MongoDB connection failed** - Check MONGO_URI
3. **Discord token invalid** - Check DISCORD_TOKEN

#### Solutions:
1. **Check runtime logs** in Render dashboard
2. **Verify environment variables** are set correctly
3. **Test MongoDB connection** separately

### Bot Not Responding

#### Common Issues:
1. **Bot not online** - Check Discord Developer Portal
2. **Missing permissions** - Check bot permissions in Discord
3. **Commands not synced** - Check slash command sync

#### Solutions:
1. **Check bot status** in Discord
2. **Verify bot permissions** in server settings
3. **Check slash command sync** in logs

## Monitoring

### Health Check Endpoints
- `/` - Basic status
- `/health` - Detailed health info
- `/metrics` - System metrics
- `/status` - Bot status
- `/ping` - Simple ping

### Logs
- **Build logs** - Available during deployment
- **Runtime logs** - Available in Render dashboard
- **Bot logs** - Written to `bot.log` file

### Performance
- **Free tier limits**: 750 hours/month
- **Auto-sleep**: Free tier sleeps after 15 minutes of inactivity
- **Wake-up time**: ~30 seconds after first request

## Security Best Practices

1. **Environment Variables** - Never commit secrets to code
2. **MongoDB Security** - Use strong passwords and IP whitelist
3. **Discord Permissions** - Only grant necessary permissions
4. **Regular Updates** - Keep dependencies updated

## Cost Optimization

### Free Tier Tips:
1. **Use auto-sleep** - Bot sleeps when not in use
2. **Monitor usage** - Stay under 750 hours/month
3. **Optimize dependencies** - Remove unused packages

### Paid Tier Benefits:
1. **Always-on** - No sleep mode
2. **More resources** - Better performance
3. **Custom domains** - Use your own domain

## Support

### Render Support:
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)

### Bot Issues:
- Check logs in Render dashboard
- Test commands locally first
- Verify all environment variables

## Success Checklist

- [ ] Repository pushed to GitHub
- [ ] Render web service created
- [ ] Environment variables set
- [ ] Build completed successfully
- [ ] Bot appears online in Discord
- [ ] Slash commands working
- [ ] Health check endpoints responding
- [ ] AutoMod integration working
- [ ] Badges appearing (after 24-48 hours)

## Quick Commands

### Local Testing:
```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py

# Test health endpoint
curl http://localhost:8080/health
```

### Render Deployment:
```bash
# Push to GitHub
git add .
git commit -m "Render deployment ready"
git push origin main

# Check deployment status
# Go to Render dashboard
```

Your bot is now 100% Render-ready! 🎉 