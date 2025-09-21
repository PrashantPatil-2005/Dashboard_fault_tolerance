# Factory Monitoring Backend - Complete Setup Guide

This comprehensive guide will walk you through setting up the Factory Monitoring Backend from scratch.

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- MongoDB (local or remote)
- SSH access to remote server (if using SSH tunnel)

## 🚀 Step-by-Step Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd factory_monitoring_backend
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017/
DATABASE_NAME=factory_db

# SSH Tunnel Configuration (Optional)
USE_SSH_TUNNEL=false
SSH_HOST=your-server.com
SSH_PORT=22
SSH_USERNAME=ubuntu
SSH_KEY_PATH=/path/to/your/ssh/key.pem
REMOTE_MONGODB_HOST=localhost
REMOTE_MONGODB_PORT=27017
LOCAL_MONGODB_PORT=27017

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# External API Configuration
EXTERNAL_API_BASE_URL=https://srcapiv2.aams.io/AAMS/AI

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### Step 5: Test Database Connection

```bash
# Test connection
python scripts/test_connection.py
```

### Step 6: Run the Application

#### Option A: Development Mode (Recommended for testing)
```bash
python start_server.py
```

#### Option B: With SSH Tunnel (for remote MongoDB)
```bash
# Set environment variable
export USE_SSH_TUNNEL=true  # Linux/Mac
set USE_SSH_TUNNEL=true     # Windows

# Run with SSH tunnel
python scripts/start_with_ssh_tunnel.py
```

#### Option C: Production Mode
```bash
python run.py prod
```

### Step 7: Verify Installation

1. **Check Health**: http://localhost:8000/health
2. **API Documentation**: http://localhost:8000/docs
3. **System Stats**: http://localhost:8000/api/stats

## 🔧 Configuration Options

### MongoDB Connection Types

#### 1. Local MongoDB
```env
USE_SSH_TUNNEL=false
MONGODB_URL=mongodb://localhost:27017/
```

#### 2. Remote MongoDB (Direct)
```env
USE_SSH_TUNNEL=false
MONGODB_URL=mongodb://username:password@remote-host:27017/
```

#### 3. Remote MongoDB (SSH Tunnel)
```env
USE_SSH_TUNNEL=true
SSH_HOST=your-server.com
SSH_USERNAME=ubuntu
SSH_KEY_PATH=/path/to/ssh/key.pem
REMOTE_MONGODB_HOST=localhost
REMOTE_MONGODB_PORT=27017
```

### API Configuration

#### Development
```env
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=DEBUG
```

#### Production
```env
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

## 📊 Data Management

### Export Data
```bash
# Export all data
python scripts/export_data.py --type all

# Export specific data
python scripts/export_data.py --type machines
python scripts/export_data.py --type data
```

### Test Connection
```bash
# Test database connection
python scripts/test_connection.py
```

## 🐛 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed
```
Failed to connect to MongoDB: localhost:27017: [WinError 10061]
```

**Solutions:**
- Ensure MongoDB is running locally
- Check MongoDB URL in `.env`
- For remote MongoDB, verify SSH tunnel settings

#### 2. SSH Tunnel Issues
```
Failed to start SSH tunnel
```

**Solutions:**
- Verify SSH key path and permissions
- Check SSH host and port
- Ensure SSH key is authorized on remote server

#### 3. Port Already in Use
```
[Errno 48] Address already in use
```

**Solutions:**
- Change port in `.env` file
- Kill existing process: `taskkill /f /im python.exe` (Windows)
- Use different port: `API_PORT=8001`

#### 4. Module Not Found
```
ModuleNotFoundError: No module named 'sshtunnel'
```

**Solutions:**
- Install dependencies: `pip install -r requirements.txt`
- Activate virtual environment

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=DEBUG
```

### Check Logs

```bash
# View application logs
tail -f app.log

# View system logs (Linux/Mac)
journalctl -u factory-monitoring-backend -f
```

## 🔒 Security Best Practices

### 1. Environment Variables
- Never commit `.env` files
- Use strong passwords
- Rotate SSH keys regularly

### 2. MongoDB Security
- Enable authentication
- Use SSL/TLS in production
- Configure firewall rules

### 3. API Security
- Configure CORS appropriately
- Use HTTPS in production
- Implement rate limiting

## 📈 Performance Optimization

### 1. Database
- Create appropriate indexes
- Use connection pooling
- Monitor query performance

### 2. API
- Enable response caching
- Use async operations
- Monitor memory usage

### 3. SSH Tunnel
- Use persistent connections
- Monitor tunnel health
- Implement reconnection logic

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "start_server.py"]
```

### Systemd Service (Linux)
```ini
[Unit]
Description=Factory Monitoring Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/factory_monitoring_backend
ExecStart=/usr/bin/python3 start_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Test database connection
4. Verify configuration settings

## 🔄 Updates

To update the application:

```bash
git pull origin main
pip install -r requirements.txt
python scripts/test_connection.py
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [SSH Tunnel Guide](SSH_TUNNEL_GUIDE.md)
- [API Documentation](http://localhost:8000/docs) (when running)
