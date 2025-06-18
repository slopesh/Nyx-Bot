@echo off
echo 🚀 Minecraft Proxy Bot Deployment Script
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip first.
    pause
    exit /b 1
)

echo ✅ Python and pip are installed

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating template...
    (
        echo # Discord Bot Configuration
        echo DISCORD_TOKEN=your_discord_bot_token_here
        echo MONGO_URI=your_mongodb_connection_string_here
        echo WATCH_URL=your_minecraft_proxy_url_here
        echo DISCORD_CHANNEL_ID=your_discord_channel_id_here
        echo.
        echo # Optional Configuration
        echo ENVIRONMENT=development
    ) > .env
    echo 📝 Please edit the .env file with your actual values before running the bot.
) else (
    echo ✅ .env file found
)

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your actual values
echo 2. Run: python bot.py
echo.
echo For Render deployment:
echo 1. Push this code to GitHub
echo 2. Connect your repo to Render
echo 3. Add environment variables in Render dashboard
echo 4. Deploy!
echo.
echo For local testing:
echo venv\Scripts\activate.bat
echo python bot.py
pause 