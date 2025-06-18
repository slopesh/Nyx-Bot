from flask import Flask, jsonify
from threading import Thread
import time
import psutil
import os
from datetime import datetime
import gc
import logging
from logging.handlers import RotatingFileHandler
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('bot.log', maxBytes=1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask('')

# Global variables for monitoring
start_time = time.time()
last_health_check = time.time()
last_gc_time = time.time()
memory_threshold = 85  # Percentage

# Get port from environment variable (Render sets PORT)
PORT = int(os.environ.get('PORT', 8080))

# Configure requests session with retry strategy
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

def check_memory():
    """Check memory usage and force garbage collection if needed"""
    global last_gc_time
    try:
        memory = psutil.virtual_memory()
        
        if memory.percent > memory_threshold:
            logger.warning(f"High memory usage detected: {memory.percent}%")
            gc.collect()
            last_gc_time = time.time()
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking memory: {e}")
        return False

@app.route('/')
def home():
    try:
        check_memory()
        return jsonify({
            "status": "online",
            "message": "Minecraft Proxy Bot is running!",
            "uptime": f"{int((time.time() - start_time) // 3600)}h {int(((time.time() - start_time) % 3600) // 60)}m",
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health')
def health():
    try:
        global last_health_check
        last_health_check = time.time()
        
        # Get system stats
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Calculate uptime
        uptime = time.time() - start_time
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        
        # Check memory and force GC if needed
        memory_warning = check_memory()
        
        response = {
            "status": "healthy",
            "uptime": f"{days}d {hours}h {minutes}m",
            "cpu_usage": f"{cpu_percent}%",
            "memory_usage": f"{memory.percent}%",
            "disk_usage": f"{disk.percent}%",
            "last_health_check": datetime.fromtimestamp(last_health_check).strftime('%Y-%m-%d %H:%M:%S'),
            "memory_warning": memory_warning,
            "last_gc": datetime.fromtimestamp(last_gc_time).strftime('%Y-%m-%d %H:%M:%S'),
            "environment": os.getenv('ENVIRONMENT', 'production'),
            "port": PORT
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/metrics')
def metrics():
    try:
        # Get detailed system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()
        
        # Check memory and force GC if needed
        check_memory()
        
        return jsonify({
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            },
            "bot": {
                "uptime": time.time() - start_time,
                "port": PORT,
                "environment": os.getenv('ENVIRONMENT', 'production')
            }
        })
    except Exception as e:
        logger.error(f"Error in metrics: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status')
def status():
    try:
        # Check if bot is responsive
        time_since_last_health = time.time() - last_health_check
        is_healthy = time_since_last_health < 300  # 5 minutes threshold
        
        # Check memory
        memory_warning = check_memory()
        
        return jsonify({
            "status": "online" if is_healthy else "degraded",
            "last_health_check": datetime.fromtimestamp(last_health_check).strftime('%Y-%m-%d %H:%M:%S'),
            "time_since_last_health": f"{int(time_since_last_health)}s",
            "environment": os.getenv('ENVIRONMENT', 'production'),
            "memory_warning": memory_warning,
            "port": PORT
        })
    except Exception as e:
        logger.error(f"Error in status check: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/ping')
def ping():
    """Simple ping endpoint for health checks"""
    return jsonify({"pong": True, "timestamp": datetime.utcnow().isoformat()})

def run():
    """Run the Flask server"""
    while True:
        try:
            logger.info(f"Starting Flask server on port {PORT}")
            # Use 0.0.0.0 to make the server publicly available (required for Render)
            app.run(host='0.0.0.0', port=PORT, debug=False)
        except Exception as e:
            logger.error(f"Error starting Flask server: {e}")
            # Retry after 5 seconds
            time.sleep(5)
            # Force garbage collection before retry
            gc.collect()

def keep_alive():
    """Start the keep-alive server in a separate thread"""
    logger.info("Starting keep-alive server...")
    t = Thread(target=run)
    t.daemon = True  # Make thread daemon so it exits when main program exits
    t.start()
    
    # Start a background thread for periodic memory checks
    def memory_monitor():
        while True:
            try:
                check_memory()
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Error in memory monitor: {e}")
                time.sleep(60)  # Wait a minute before retrying
    
    monitor_thread = Thread(target=memory_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    logger.info("Keep-alive server started successfully") 