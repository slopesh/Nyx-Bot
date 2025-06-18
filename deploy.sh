#!/bin/bash

echo "🚀 Minecraft Proxy Bot Deployment Script"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ Python and pip are installed"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
MONGO_URI=your_mongodb_connection_string_here
WATCH_URL=your_minecraft_proxy_url_here
DISCORD_CHANNEL_ID=your_discord_channel_id_here

# Optional Configuration
ENVIRONMENT=development
EOF
    echo "📝 Please edit the .env file with your actual values before running the bot."
else
    echo "✅ .env file found"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your actual values"
echo "2. Run: python bot.py"
echo ""
echo "For Render deployment:"
echo "1. Push this code to GitHub"
echo "2. Connect your repo to Render"
echo "3. Add environment variables in Render dashboard"
echo "4. Deploy!"
echo ""
echo "For local testing:"
echo "source venv/bin/activate"
echo "python bot.py" 